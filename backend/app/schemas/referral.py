from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import ORMBase


class ReferralCreate(BaseModel):
    referrer_id: int
    referee_id: int
    commission_rate: Decimal


class ReferralResponse(ORMBase):
    id: int
    referrer_id: int
    referee_id: int
    referrer_name: str | None = None
    referee_name: str | None = None
    commission_rate: Decimal
    total_earned: Decimal
    created_at: datetime
