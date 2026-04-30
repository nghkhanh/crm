from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.invoice import InvoiceStatus
from app.schemas.common import ORMBase


class InvoiceGenerateRequest(BaseModel):
    customer_id: int
    period_start: date
    period_end: date


class InvoiceStatusUpdate(BaseModel):
    status: InvoiceStatus
    file_url: str | None = None


class InvoiceResponse(ORMBase):
    id: int
    customer_id: int
    invoice_number: str | None = None
    period_start: date
    period_end: date
    total_topup: Decimal
    total_fee: Decimal
    total_commission: Decimal
    file_url: str | None = None
    status: InvoiceStatus
    sent_at: datetime | None = None
    paid_at: datetime | None = None
    locked_at: datetime | None = None
    created_at: datetime
