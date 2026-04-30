from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.transaction import TransactionSource, TransactionStatus, TransactionType
from app.schemas.common import ORMBase


class TransactionCreate(BaseModel):
    customer_id: int
    type: TransactionType
    amount: Decimal
    reference: str | None = None
    note: str | None = None


class TransactionResponse(ORMBase):
    id: int
    customer_id: int
    type: TransactionType
    source: TransactionSource
    status: TransactionStatus
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    reference: str | None = None
    note: str | None = None
    created_by: int | None = None
    created_at: datetime
