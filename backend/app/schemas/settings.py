from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, field_validator

from app.schemas.common import ORMBase


class SystemSettingResponse(ORMBase):
    id: int
    key: str
    value: str
    description: str | None = None
    created_at: datetime


class SystemSettingsUpdate(BaseModel):
    fb_system_user_token: str = ""
    fb_business_id: str = ""
    lark_webhook_url: str = ""
    backend_public_base_url: str = ""
    frontend_public_base_url: str = ""
    agency_usdt_wallet: str = ""
    trongrid_api_key: str = ""
    sepay_webhook_secret: str = ""
    default_commission_rate: str = "5"

    @field_validator(
        "fb_system_user_token",
        "fb_business_id",
        "agency_usdt_wallet",
        "trongrid_api_key",
        "sepay_webhook_secret",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: str) -> str:
        return str(value or "").strip()

    @field_validator("lark_webhook_url", mode="before")
    @classmethod
    def validate_lark_webhook_url(cls, value: str) -> str:
        value = str(value or "").strip()
        if not value:
            return ""
        AnyHttpUrl(value)
        return value

    @field_validator("backend_public_base_url", "frontend_public_base_url", mode="before")
    @classmethod
    def validate_public_base_url(cls, value: str) -> str:
        value = str(value or "").strip()
        if not value:
            return ""
        AnyHttpUrl(value)
        return value.rstrip("/")

    @field_validator("fb_business_id")
    @classmethod
    def validate_business_id(cls, value: str) -> str:
        if value and not value.isdigit():
            raise ValueError("Facebook business ID must be numeric")
        return value

    @field_validator("agency_usdt_wallet")
    @classmethod
    def validate_tron_wallet(cls, value: str) -> str:
        if value and (len(value) != 34 or not value.startswith("T")):
            raise ValueError("Agency USDT wallet must be a valid TRON address")
        return value

    @field_validator("default_commission_rate")
    @classmethod
    def validate_commission_rate(cls, value: str) -> str:
        normalized = str(value or "").strip() or "0"
        try:
            numeric = float(normalized)
        except ValueError as exc:
            raise ValueError("Default commission rate must be numeric") from exc
        if numeric < 0 or numeric > 100:
            raise ValueError("Default commission rate must be between 0 and 100")
        return f"{numeric:g}"
