import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.integrations import FacebookValidationResponse, IntegrationHealthResponse
from app.services.settings import SettingsService

try:
    from facebook_business.api import FacebookAdsApi
except Exception:  # pragma: no cover
    FacebookAdsApi = None


class IntegrationHealthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_all(self) -> list[IntegrationHealthResponse]:
        settings_map = await SettingsService(self.session).get_settings_map()
        return [
            await self.check_facebook(settings_map),
            await self.check_lark(settings_map),
            await self.check_sepay(settings_map),
            await self.check_trongrid(settings_map),
        ]

    async def validate_facebook_credentials(self) -> FacebookValidationResponse:
        settings_map = await SettingsService(self.session).get_settings_map()
        token = settings_map.get("fb_system_user_token", "")
        business_id = settings_map.get("fb_business_id", "")
        if not token or not business_id:
            return FacebookValidationResponse(valid=False, business_id=business_id, message="Missing token or business ID")
        if not FacebookAdsApi:
            return FacebookValidationResponse(valid=False, business_id=business_id, message="Facebook SDK not available")
        try:
            FacebookAdsApi.init(access_token=token)
            async with httpx.AsyncClient(timeout=20) as client:
                business_response = await client.get(
                    f"https://graph.facebook.com/v20.0/{business_id}",
                    params={"access_token": token, "fields": "id,name"},
                )
                business_response.raise_for_status()
                business_payload = business_response.json()
                ad_accounts_response = await client.get(
                    f"https://graph.facebook.com/v20.0/{business_id}/owned_ad_accounts",
                    params={"access_token": token, "limit": 1, "summary": "true"},
                )
                ad_accounts_response.raise_for_status()
                ad_accounts_payload = ad_accounts_response.json()
            return FacebookValidationResponse(
                valid=True,
                business_id=str(business_payload.get("id", business_id)),
                business_name=business_payload.get("name"),
                ad_accounts_count=(ad_accounts_payload.get("summary") or {}).get("total_count"),
                message="Facebook credentials are valid and business is reachable",
            )
        except Exception as exc:
            return FacebookValidationResponse(valid=False, business_id=business_id, message=str(exc))

    async def check_facebook(self, settings_map: dict[str, str]) -> IntegrationHealthResponse:
        token = settings_map.get("fb_system_user_token", "")
        business_id = settings_map.get("fb_business_id", "")
        if not token or not business_id:
            return IntegrationHealthResponse(name="facebook", configured=False, reachable=False, message="Missing token or business ID")
        if not FacebookAdsApi:
            return IntegrationHealthResponse(name="facebook", configured=True, reachable=False, message="Facebook SDK not available")
        try:
            FacebookAdsApi.init(access_token=token)
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    f"https://graph.facebook.com/v20.0/{business_id}",
                    params={"access_token": token, "fields": "id,name"},
                )
                response.raise_for_status()
            return IntegrationHealthResponse(name="facebook", configured=True, reachable=True, message="Facebook API reachable")
        except Exception as exc:
            return IntegrationHealthResponse(name="facebook", configured=True, reachable=False, message=str(exc))

    async def check_lark(self, settings_map: dict[str, str]) -> IntegrationHealthResponse:
        webhook = settings_map.get("lark_webhook_url", "")
        if not webhook:
            return IntegrationHealthResponse(name="lark", configured=False, reachable=False, message="Missing webhook URL")
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(webhook, json={"msg_type": "text", "content": {"text": "CRM integration health check"}})
                response.raise_for_status()
            return IntegrationHealthResponse(name="lark", configured=True, reachable=True, message="Lark webhook reachable")
        except Exception as exc:
            return IntegrationHealthResponse(name="lark", configured=True, reachable=False, message=str(exc))

    async def check_sepay(self, settings_map: dict[str, str]) -> IntegrationHealthResponse:
        secret = settings_map.get("sepay_webhook_secret", "")
        if not secret:
            return IntegrationHealthResponse(name="sepay", configured=False, reachable=False, message="Missing webhook secret")
        return IntegrationHealthResponse(name="sepay", configured=True, reachable=True, message="Webhook secret configured")

    async def check_trongrid(self, settings_map: dict[str, str]) -> IntegrationHealthResponse:
        wallet = settings_map.get("agency_usdt_wallet", "")
        api_key = settings_map.get("trongrid_api_key", "")
        if not wallet or not api_key:
            return IntegrationHealthResponse(name="trongrid", configured=False, reachable=False, message="Missing wallet or API key")
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    f"https://api.trongrid.io/v1/accounts/{wallet}",
                    headers={"TRON-PRO-API-KEY": api_key},
                )
                response.raise_for_status()
            return IntegrationHealthResponse(name="trongrid", configured=True, reachable=True, message="TronGrid reachable")
        except Exception as exc:
            return IntegrationHealthResponse(name="trongrid", configured=True, reachable=False, message=str(exc))
