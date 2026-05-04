from datetime import datetime, timezone
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bank_treasury_snapshot import BankTreasuryProvider, BankTreasurySnapshot
from app.services.settings import SettingsService


class BankTreasuryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_snapshots(self) -> list[BankTreasurySnapshot]:
        result = await self.session.execute(select(BankTreasurySnapshot).order_by(BankTreasurySnapshot.synced_at.desc()))
        return list(result.scalars().all())

    async def sync_sepay_balance(self) -> BankTreasurySnapshot:
        settings_map = await SettingsService(self.session).get_settings_map()
        api_token = settings_map.get("sepay_api_token", "")
        bank_account_id = settings_map.get("sepay_bank_account_id", "")
        if not api_token or not bank_account_id:
            raise ValueError("SePay API token hoặc Bank Account ID chưa được cấu hình.")

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"https://my.sepay.vn/userapi/bankaccounts/details/{bank_account_id}",
                headers={"Authorization": f"Bearer {api_token}", "Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()

        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, dict):
            data = payload if isinstance(payload, dict) else {}

        snapshot = BankTreasurySnapshot(
            provider=BankTreasuryProvider.sepay,
            bank_account_id=bank_account_id,
            account_number=str(data.get("account_number") or data.get("accountNumber") or ""),
            account_name=data.get("account_holder_name") or data.get("accountName") or data.get("account_holder"),
            currency=str(data.get("currency") or "VND"),
            balance=Decimal(str(data.get("balance") or data.get("account_balance") or "0")),
            available_balance=Decimal(str(data.get("available_balance"))) if data.get("available_balance") not in (None, "") else None,
            status_message=str(data.get("status") or "Synced"),
            raw_payload=data,
            synced_at=datetime.now(timezone.utc),
        )
        self.session.add(snapshot)
        await self.session.commit()
        await self.session.refresh(snapshot)
        return snapshot

