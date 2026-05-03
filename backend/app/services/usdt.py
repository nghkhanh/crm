from datetime import datetime, timezone
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.customer_usdt_address import CustomerUsdtAddress, UsdtAddressStatus
from app.models.payment_reconciliation import ReconciliationChannel, ReconciliationStatus
from app.models.transaction import Transaction, TransactionSource, TransactionStatus, TransactionType
from app.services.reconciliation import ReconciliationService
from app.services.audit import write_audit_log
from app.services.settings import SettingsService
from app.services.webhook_events import WebhookEventService


class USDTService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def poll_transactions(self) -> dict[str, int]:
        settings_map = await SettingsService(self.session).get_settings_map()
        trongrid_api_key = settings_map.get("trongrid_api_key", "")
        usdt_contract = settings_map.get("usdt_trc20_contract", "")
        if not trongrid_api_key:
            return {"processed": 0}
        processed = 0
        event_service = WebhookEventService(self.session)
        active_addresses = (
            await self.session.execute(
                select(CustomerUsdtAddress)
                .where(CustomerUsdtAddress.status == UsdtAddressStatus.active)
                .options()
            )
        ).scalars().all()
        if not active_addresses:
            return {"processed": 0}

        headers = {"TRON-PRO-API-KEY": trongrid_api_key}
        async with httpx.AsyncClient(timeout=20) as client:
            for deposit_address in active_addresses:
                url = f"https://api.trongrid.io/v1/accounts/{deposit_address.address}/transactions/trc20"
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                transactions = response.json().get("data", [])
                for item in transactions[:20]:
                    tx_id = item.get("transaction_id", "")
                    if not tx_id:
                        continue
                    if usdt_contract and (item.get("token_info") or {}).get("address") not in {"", usdt_contract}:
                        continue
                    if item.get("confirmed") is False:
                        continue
                    if await event_service.already_processed("trongrid", tx_id):
                        await ReconciliationService(self.session).create_record(
                            channel=ReconciliationChannel.usdt,
                            status=ReconciliationStatus.duplicate,
                            external_id=tx_id,
                            amount=Decimal(item.get("value", "0")) / Decimal("1000000"),
                            customer_id=deposit_address.customer_id,
                            reference=tx_id,
                            wallet_address=deposit_address.address,
                            raw_payload=item,
                        )
                        continue
                    destination = (item.get("to") or "").strip()
                    if destination and destination != deposit_address.address:
                        continue
                    amount = Decimal(item.get("value", "0")) / Decimal("1000000")
                    if amount <= 0:
                        continue
                    customer = await self.session.get(Customer, deposit_address.customer_id)
                    if not customer:
                        continue
                    balance_before = Decimal(customer.wallet_balance)
                    customer.wallet_balance += amount
                    deposit_address.last_seen_at = datetime.now(timezone.utc)
                    transaction = Transaction(
                        customer_id=customer.id,
                        type=TransactionType.topup_usdt,
                        source=TransactionSource.trongrid,
                        status=TransactionStatus.posted,
                        amount=amount,
                        balance_before=balance_before,
                        balance_after=Decimal(customer.wallet_balance),
                        reference=tx_id,
                        note=f"Auto topup via TronGrid deposit address {deposit_address.address}",
                    )
                    self.session.add(transaction)
                    await self.session.flush()
                    await ReconciliationService(self.session).create_record(
                        channel=ReconciliationChannel.usdt,
                        status=ReconciliationStatus.credited,
                        external_id=tx_id,
                        amount=amount,
                        customer_id=customer.id,
                        transaction_id=transaction.id,
                        reference=tx_id,
                        wallet_address=deposit_address.address,
                        raw_payload=item,
                    )
                    await event_service.record(
                        source="trongrid",
                        event_type="topup_usdt",
                        external_id=tx_id,
                        payload_json={
                            "transaction_id": tx_id,
                            "amount": str(amount),
                            "deposit_address": deposit_address.address,
                            "customer_id": customer.id,
                        },
                    )
                    await write_audit_log(
                        self.session,
                        user_id=None,
                        action="webhook.trongrid_processed",
                        entity_type="transaction",
                        entity_id=transaction.id,
                        metadata_json={
                            "customer_id": customer.id,
                            "reference": tx_id,
                            "amount": str(amount),
                            "deposit_address": deposit_address.address,
                        },
                    )
                    processed += 1

        await self.session.commit()
        return {"processed": processed}
