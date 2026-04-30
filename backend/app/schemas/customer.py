from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr

from app.models.customer import CustomerStatus
from app.schemas.common import ORMBase
from app.schemas.usdt_address import CustomerUsdtAddressResponse


class CustomerCreate(BaseModel):
    full_name: str
    email: EmailStr | None = None
    phone: str | None = None
    telegram_id: str | None = None
    referral_code: str | None = None
    referred_by: int | None = None
    wallet_balance: Decimal = Decimal("0.00")
    status: CustomerStatus = CustomerStatus.active
    note: str | None = None


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
