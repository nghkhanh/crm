from datetime import datetime
from decimal import Decimal

from app.models.payment_reconciliation import ReconciliationChannel, ReconciliationStatus
from app.schemas.common import ORMBase


class ReconciliationResponse(ORMBase):
    id: int
    channel: ReconciliationChannel
    status: ReconciliationStatus
    customer_id: int | None = None
    transaction_id: int | None = None
    external_id: str
    amount: Decimal
    reference: str | None = None
    wallet_address: str | None = None
    note: str | None = None
    raw_payload: dict
    created_at: datetime
