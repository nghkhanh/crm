from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SqlEnum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class InvoiceStatus(str, Enum):
    draft = "draft"
    sent = "sent"
    paid = "paid"


class Invoice(TimestampMixin, Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    invoice_number: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, index=True)
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    total_topup: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    total_fee: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    total_commission: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[InvoiceStatus] = mapped_column(SqlEnum(InvoiceStatus, name="invoice_status"), default=InvoiceStatus.draft)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer = relationship("Customer", back_populates="invoices")
