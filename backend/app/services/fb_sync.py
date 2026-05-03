import logging
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad_account import AdAccount, AdAccountStatus, AdSpendProvider, FacebookPaymentStatus, Platform
from app.services.settings import SettingsService
from app.services.smit_sync import SmitSyncService

logger = logging.getLogger(__name__)

try:
    from facebook_business.adobjects.adaccount import AdAccount as FacebookAdAccount
    from facebook_business.api import FacebookAdsApi
except Exception:  # pragma: no cover
    FacebookAdAccount = None
    FacebookAdsApi = None


class FacebookSyncService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def sync_accounts(self) -> dict[str, int]:
        result = await self.session.execute(select(AdAccount).where(AdAccount.platform == Platform.facebook))
        accounts = result.scalars().all()
        synced = 0
        failed = 0
        settings_map = await SettingsService(self.session).get_settings_map()
        fb_system_user_token = settings_map.get("fb_system_user_token", "")
        fb_business_id = settings_map.get("fb_business_id", "")
        facebook_graph_ready = bool(fb_system_user_token and fb_business_id and FacebookAdsApi)
        if facebook_graph_ready:
            FacebookAdsApi.init(access_token=fb_system_user_token)

        for account in accounts:
            try:
                if account.spend_provider == AdSpendProvider.smit:
                    await SmitSyncService(self.session).sync_account(account)
                else:
                    if not facebook_graph_ready:
                        raise RuntimeError("Facebook Graph credentials or SDK are unavailable")
                    self._sync_single_account(account)
                    account.payment_status = self._resolve_payment_status(account)
                account.last_synced_at = datetime.now(timezone.utc)
                synced += 1
            except Exception as exc:  # pragma: no cover
                failed += 1
                logger.exception("Failed syncing ad account %s: %s", account.account_id, exc)

        await self.session.commit()
        return {"synced": synced, "failed": failed}

    def _sync_single_account(self, account: AdAccount) -> None:
        fb_account = FacebookAdAccount(f"act_{account.account_id}")
        details = fb_account.api_get(fields=["name", "account_status", "amount_spent", "balance"])
        insights = fb_account.get_insights(
            fields=["spend"],
            params={"date_preset": "last_90d"},
        )
        spend_90d = sum(Decimal(item.get("spend", "0")) for item in insights)
        account.account_name = details.get("name", account.account_name)
        account.status = AdAccountStatus.active if str(details.get("account_status")) == "1" else AdAccountStatus.disabled
        account.balance = Decimal(details.get("balance", "0")) / Decimal("100")
        account.spend_today = Decimal(details.get("amount_spent", "0")) / Decimal("100")
        account.spend_7d = spend_90d
        account.spend_28d = spend_90d
        account.spend_90d = spend_90d

    @staticmethod
    def _resolve_payment_status(account: AdAccount) -> FacebookPaymentStatus:
        if Decimal(account.prepaid_balance) <= Decimal("0") or Decimal(account.amount_due) > Decimal(account.prepaid_balance):
            return FacebookPaymentStatus.overdue
        if Decimal(account.prepaid_balance) <= Decimal(account.payment_threshold):
            return FacebookPaymentStatus.due
        return FacebookPaymentStatus.healthy
