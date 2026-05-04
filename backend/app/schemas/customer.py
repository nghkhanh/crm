from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, field_validator

from app.models.customer import CustomerStatus
from app.schemas.common import ORMBase
from app.schemas.usdt_address import CustomerUsdtAddressResponse


class CustomerCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None
    telegram_id: str | None = None
    referral_code: str | None = None
    referred_by: int | None = None
    wallet_balance: Decimal = Decimal("0.00")
    status: CustomerStatus = CustomerStatus.active
    note: str | None = None

    @field_validator("full_name", mode="before")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        normalized = str(value or "").strip()
        if not normalized:
            raise ValueError("Customer name is required")
        return normalized

    @field_validator("phone", "telegram_id", "referral_code", "note", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        normalized = str(value or "").strip()
        return normalized or None

    @field_validator("email", mode="before")
    @classmethod
    def validate_email_required(cls, value: str) -> str:
        normalized = str(value or "").strip()
        if not normalized:
            raise ValueError("Email is required")
        return normalized


class CustomerUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    telegram_id: str | None = None
    referral_code: str | None = None
    referred_by: int | None = None
    wallet_balance: Decimal | None = None
    status: CustomerStatus | None = None
    note: str | None = None

    @field_validator("full_name", mode="before")
    @classmethod
    def validate_update_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip()
        if not normalized:
            raise ValueError("Customer name cannot be empty")
        return normalized

    @field_validator("phone", "telegram_id", "referral_code", "note", mode="before")
    @classmethod
    def normalize_update_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_update_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None


class CustomerResponse(ORMBase):
    id: int
    full_name: str
    email: EmailStr | None = None
    phone: str | None = None
    telegram_id: str | None = None
    referral_code: str | None = None
    referred_by: int | None = None
    wallet_balance: Decimal
    status: CustomerStatus
    note: str | None = None
    created_at: datetime


class CustomerDetailResponse(BaseModel):
    profile: CustomerResponse
    ad_accounts: list[dict]
    recent_transactions: list[dict]
    tickets: list[dict]
    usdt_addresses: list[CustomerUsdtAddressResponse]
