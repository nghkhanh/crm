from datetime import datetime, timezone
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.customer_usdt_address import CustomerUsdtAddress, UsdtAddressNetwork, UsdtAddressStatus
from app.models.usdt_wallet_inventory import (
    UsdtWalletGasStatus,
    UsdtWalletInventory,
    UsdtWalletInventoryStatus,
    UsdtWalletSweepStatus,
)
from app.services.settings import SettingsService


class UsdtWalletOpsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_wallets(self) -> list[UsdtWalletInventory]:
        result = await self.session.execute(select(UsdtWalletInventory).order_by(UsdtWalletInventory.created_at.desc()))
        return list(result.scalars().all())

    async def create_wallet(self, *, address: str, label: str | None = None, note: str | None = None) -> UsdtWalletInventory:
        existing = await self.session.scalar(select(UsdtWalletInventory).where(UsdtWalletInventory.address == address))
        if existing:
            raise ValueError("Ví này đã tồn tại trong kho.")
        wallet = UsdtWalletInventory(address=address, label=label, note=note)
        self.session.add(wallet)
        await self.session.commit()
        await self.session.refresh(wallet)
        return wallet

    async def assign_wallet(self, *, wallet_id: int, customer_id: int) -> UsdtWalletInventory:
        wallet = await self.session.get(UsdtWalletInventory, wallet_id)
        if not wallet:
            raise ValueError("Không tìm thấy ví trong kho.")
        if wallet.status != UsdtWalletInventoryStatus.available:
            raise ValueError("Ví này không còn sẵn để cấp phát.")
        customer = await self.session.get(Customer, customer_id)
        if not customer:
            raise ValueError("Không tìm thấy khách hàng.")

        address = await self.session.scalar(select(CustomerUsdtAddress).where(CustomerUsdtAddress.address == wallet.address))
        if address:
            raise ValueError("Địa chỉ ví này đã được dùng trong danh sách nạp.")

        customer_address = CustomerUsdtAddress(
            customer_id=customer_id,
            network=UsdtAddressNetwork.trc20,
            address=wallet.address,
            label=wallet.label,
            status=UsdtAddressStatus.active,
            assigned_at=datetime.now(timezone.utc),
        )
        self.session.add(customer_address)
        await self.session.flush()

        wallet.customer_id = customer_id
        wallet.customer_usdt_address_id = customer_address.id
        wallet.status = UsdtWalletInventoryStatus.assigned
        wallet.assigned_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(wallet)
        return wallet

    async def auto_assign_next_available_wallet(self, *, customer_id: int) -> UsdtWalletInventory:
        wallet = await self.session.scalar(
            select(UsdtWalletInventory)
            .where(UsdtWalletInventory.status == UsdtWalletInventoryStatus.available)
            .order_by(UsdtWalletInventory.created_at.asc())
        )
        if not wallet:
            raise ValueError("Kho ví không còn địa chỉ sẵn để cấp phát.")
        return await self.assign_wallet(wallet_id=wallet.id, customer_id=customer_id)

    async def refresh_wallet(self, wallet_id: int) -> UsdtWalletInventory:
        wallet = await self.session.get(UsdtWalletInventory, wallet_id)
        if not wallet:
            raise ValueError("Không tìm thấy ví trong kho.")

        settings_map = await SettingsService(self.session).get_settings_map()
        api_key = settings_map.get("trongrid_api_key", "")
        contract = settings_map.get("usdt_trc20_contract", "")
        trx_low_threshold = Decimal(settings_map.get("usdt_trx_low_threshold", "30") or "30")
        sweep_min_balance = Decimal(settings_map.get("usdt_sweep_min_balance", "1") or "1")
        if not api_key:
            raise ValueError("Thiếu TronGrid API key.")

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"https://api.trongrid.io/v1/accounts/{wallet.address}",
                headers={"TRON-PRO-API-KEY": api_key},
            )
            response.raise_for_status()
            payload = response.json()

        data = (payload.get("data") or [{}])[0] if isinstance(payload, dict) else {}
        trx_balance = Decimal(str(data.get("balance") or "0")) / Decimal("1000000")
        usdt_balance = Decimal("0")
        trc20_balances = data.get("trc20") or []
        if isinstance(trc20_balances, list):
            for item in trc20_balances:
                if not isinstance(item, dict):
                    continue
                for token_address, balance in item.items():
                    if contract and token_address != contract:
                        continue
                    usdt_balance = Decimal(str(balance or "0"))
                    break
                if usdt_balance > 0:
                    break

        wallet.trx_balance = trx_balance
        wallet.usdt_balance = usdt_balance
        wallet.last_balance_synced_at = datetime.now(timezone.utc)
        if trx_balance <= 0:
            wallet.gas_status = UsdtWalletGasStatus.missing
        elif trx_balance < trx_low_threshold:
            wallet.gas_status = UsdtWalletGasStatus.low
        else:
            wallet.gas_status = UsdtWalletGasStatus.ok

        if wallet.status == UsdtWalletInventoryStatus.assigned and usdt_balance >= sweep_min_balance:
            if wallet.sweep_status != UsdtWalletSweepStatus.pending:
                wallet.sweep_status = UsdtWalletSweepStatus.ready
        elif wallet.sweep_status != UsdtWalletSweepStatus.pending:
            wallet.sweep_status = UsdtWalletSweepStatus.idle

        await self.session.commit()
        await self.session.refresh(wallet)
        return wallet

    async def queue_sweep(self, *, wallet_id: int, note: str | None = None) -> UsdtWalletInventory:
        wallet = await self.session.get(UsdtWalletInventory, wallet_id)
        if not wallet:
            raise ValueError("Không tìm thấy ví trong kho.")
        settings_map = await SettingsService(self.session).get_settings_map()
        destination = settings_map.get("agency_usdt_wallet", "")
        if not destination:
            raise ValueError("Chưa cấu hình ví USDT chính của agency.")

        wallet.sweep_destination = destination
        wallet.sweep_status = UsdtWalletSweepStatus.pending
        wallet.requested_sweep_at = datetime.now(timezone.utc)
        if note:
            wallet.note = note
        await self.session.commit()
        await self.session.refresh(wallet)
        return wallet

