from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.ad_account import AdAccountStatus, AdSpendProvider, FacebookPaymentStatus, Platform
from app.schemas.common import ORMBase


class AdAccountCreate(BaseModel):
    customer_id: int
    platform: Platform
    account_id: str
    account_name: str
    status: AdAccountStatus = AdAccountStatus.active
    balance: Decimal = Decimal("0.00")
    spend_today: Decimal = Decimal("0.00")
    spend_7d: Decimal = Decimal("0.00")
    spend_28d: Decimal = Decimal("0.00")
    spend_90d: Decimal = Decimal("0.00")
    business_license_name: str | None = None
    request_id: str | None = None
    team_id: str | None = None
    spend_provider: AdSpendProvider = AdSpendProvider.facebook_graph
    amount_due: Decimal = Decimal("0.00")
    prepaid_balance: Decimal = Decimal("0.00")
    payment_threshold: Decimal = Decimal("0.00")
    payment_status: FacebookPaymentStatus = FacebookPaymentStatus.healthy


class AdAccountUpdate(BaseModel):
    account_name: str | None = None
    status: AdAccountStatus | None = None
    balance: Decimal | None = None
    business_license_name: str | None = None
    request_id: str | None = None
    team_id: str | None = None
    spend_provider: AdSpendProvider | None = None
    amount_due: Decimal | None = None
    prepaid_balance: Decimal | None = None
    payment_threshold: Decimal | None = None
    payment_status: FacebookPaymentStatus | None = None


class AdAccountResponse(ORMBase):
    id: int
    customer_id: int
    platform: Platform
    account_id: str
    account_name: str
    status: AdAccountStatus
    balance: Decimal
    spend_today: Decimal
    spend_7d: Decimal
    spend_28d: Decimal
    spend_90d: Decimal
    business_license_name: str | None = None
    request_id: str | None = None
    team_id: str | None = None
    spend_provider: AdSpendProvider
    amount_due: Decimal
    prepaid_balance: Decimal
    payment_threshold: Decimal
    payment_status: FacebookPaymentStatus
    last_payment_at: datetime | None = None
    last_synced_at: datetime | None = None
    created_at: datetime
