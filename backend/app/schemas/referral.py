from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, model_validator

from app.schemas.common import ORMBase


class ReferralCreate(BaseModel):
    referrer_id: int
    referee_id: int
    commission_rate: Decimal

    @model_validator(mode="after")
    def validate_participants(self):
        if self.referrer_id == self.referee_id:
            raise ValueError("Người giới thiệu và người được giới thiệu phải khác nhau.")
        return self


class ReferralUpdate(BaseModel):
    referrer_id: int
    referee_id: int
    commission_rate: Decimal

    @model_validator(mode="after")
    def validate_participants(self):
        if self.referrer_id == self.referee_id:
            raise ValueError("Người giới thiệu và người được giới thiệu phải khác nhau.")
        return self


class ReferralResponse(ORMBase):
    id: int
    referrer_id: int
    referee_id: int
    referrer_name: str | None = None
    referee_name: str | None = None
    commission_rate: Decimal
    total_earned: Decimal
    created_at: datetime
