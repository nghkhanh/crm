from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.ad_account import AdAccountStatus, Platform
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


class AdAccountUpdate(BaseModel):
    account_name: str | None = None
    status: AdAccountStatus | None = None
    balance: Decimal | None = None
    business_license_name: str | None = None
    request_id: str | None = None
    team_id: str | None = None


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
    last_synced_at: datetime | None = None
    created_at: datetime

