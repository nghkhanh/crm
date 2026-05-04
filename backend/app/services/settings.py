from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings as env_settings
from app.models.system_setting import SystemSetting
from app.schemas.settings import SystemSettingsUpdate


SETTING_KEYS: dict[str, str] = {
    "fb_system_user_token": "Facebook system user token",
    "fb_business_id": "Facebook business ID",
    "lark_webhook_url": "Lark incoming webhook URL",
    "backend_public_base_url": "Public backend base URL for callbacks",
    "frontend_public_base_url": "Public frontend base URL for detail links",
    "agency_usdt_wallet": "Agency USDT wallet address",
    "trongrid_api_key": "TronGrid API key",
    "usdt_trc20_contract": "USDT TRC20 contract address used for deposit validation",
    "usdt_trx_low_threshold": "Minimum TRX balance before wallet is flagged as low gas",
    "usdt_sweep_min_balance": "Minimum USDT balance before wallet is flagged as ready to sweep",
    "sepay_webhook_secret": "SePay webhook secret",
    "sepay_api_token": "SePay API token for bank account balance checks",
    "sepay_bank_account_id": "SePay bank account ID to track company bank balance",
    "smit_base_url": "SMIT API base URL",
    "smit_api_key": "SMIT API key",
    "smit_sync_url_template": "SMIT sync URL template with {account_id} placeholder",
    "default_commission_rate": "Default referral commission rate",
}


class SettingsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def ensure_defaults(self) -> None:
        result = await self.session.execute(select(SystemSetting.key))
        existing_keys = set(result.scalars().all())
        for key, description in SETTING_KEYS.items():
            if key in existing_keys:
                continue
            env_value = getattr(env_settings, key, "")
            self.session.add(SystemSetting(key=key, value=str(env_value or ""), description=description))
        await self.session.commit()

    async def list_settings(self) -> list[SystemSetting]:
        await self.ensure_defaults()
        result = await self.session.execute(select(SystemSetting).order_by(SystemSetting.key.asc()))
        return list(result.scalars().all())

    async def get_settings_map(self) -> dict[str, str]:
        items = await self.list_settings()
        return {item.key: item.value for item in items}

    async def update_settings(self, payload: SystemSettingsUpdate) -> list[SystemSetting]:
        await self.ensure_defaults()
        data = payload.model_dump()
        result = await self.session.execute(select(SystemSetting).where(SystemSetting.key.in_(list(data.keys()))))
        existing = {item.key: item for item in result.scalars().all()}
        for key, value in data.items():
            if key in existing:
                existing[key].value = value or ""
            else:
                self.session.add(SystemSetting(key=key, value=value or "", description=SETTING_KEYS.get(key)))
        await self.session.commit()
        return await self.list_settings()
