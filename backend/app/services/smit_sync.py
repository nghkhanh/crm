from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad_account import AdAccount, AdAccountStatus, FacebookPaymentStatus
from app.services.settings import SettingsService


def _parse_decimal(value: object, default: str = "0") -> Decimal:
    if value in (None, ""):
        return Decimal(default)
    return Decimal(str(value))


def _parse_datetime(value: object) -> datetime | None:
    if not value:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


class SmitSyncService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def sync_account(self, account: AdAccount) -> None:
        settings_map = await SettingsService(self.session).get_settings_map()
        base_url = settings_map.get("smit_base_url", "")
        api_key = settings_map.get("smit_api_key", "")
        url_template = settings_map.get("smit_sync_url_template", "")
        if not base_url or not api_key or not url_template:
            raise RuntimeError("SMIT settings are incomplete")

        if url_template.startswith("http://") or url_template.startswith("https://"):
            url = url_template.format(account_id=account.account_id)
        else:
            url = f"{base_url.rstrip('/')}{url_template.format(account_id=account.account_id)}"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            payload = response.json()

        if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
            payload = payload["data"]

        account.account_name = str(payload.get("name") or payload.get("account_name") or account.account_name)
        status_value = str(payload.get("status") or payload.get("account_status") or "").lower()
        account.status = AdAccountStatus.active if status_value in {"1", "active", "enabled"} else AdAccountStatus.disabled
        account.balance = _parse_decimal(payload.get("balance"), str(account.balance))
        account.spend_today = _parse_decimal(payload.get("spend_today"), str(account.spend_today))
        account.spend_7d = _parse_decimal(payload.get("spend_7d"), str(account.spend_7d))
        account.spend_28d = _parse_decimal(payload.get("spend_28d"), str(account.spend_28d))
        account.spend_90d = _parse_decimal(payload.get("spend_90d"), str(account.spend_90d))
        account.amount_due = _parse_decimal(payload.get("amount_due") or payload.get("fb_amount_due"), str(account.amount_due))
        account.prepaid_balance = _parse_decimal(
            payload.get("prepaid_balance") or payload.get("fb_prepaid_balance"),
            str(account.prepaid_balance),
        )
        account.payment_threshold = _parse_decimal(
            payload.get("payment_threshold") or payload.get("fb_payment_threshold"),
            str(account.payment_threshold),
        )
        account.last_payment_at = _parse_datetime(payload.get("last_payment_at")) or account.last_payment_at
        account.payment_status = self.resolve_payment_status(account)
        account.last_synced_at = datetime.now(timezone.utc)

    @staticmethod
    def resolve_payment_status(account: AdAccount) -> FacebookPaymentStatus:
        if Decimal(account.prepaid_balance) <= Decimal("0") or Decimal(account.amount_due) > Decimal(account.prepaid_balance):
            return FacebookPaymentStatus.overdue
        if Decimal(account.prepaid_balance) <= Decimal(account.payment_threshold):
            return FacebookPaymentStatus.due
        return FacebookPaymentStatus.healthy
