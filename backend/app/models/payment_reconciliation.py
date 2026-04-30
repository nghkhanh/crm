from decimal import Decimal
from enum import Enum

from sqlalchemy import Enum as SqlEnum, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ReconciliationChannel(str, Enum):
    bank = "bank"
    usdt = "usdt"


class ReconciliationStatus(str, Enum):
    credited = "credited"
    unmatched = "unmatched"
    duplicate = "duplicate"
    ignored = "ignored"


class PaymentReconciliation(TimestampMixin, Base):
    __tablename__ = "payment_reconciliations"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel: Mapped[ReconciliationChannel] = mapped_column(SqlEnum(ReconciliationChannel, name="reconciliation_channel"))
    status: Mapped[ReconciliationStatus] = mapped_column(SqlEnum(ReconciliationStatus, name="reconciliation_status"))
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True, index=True)
    transaction_id: Mapped[int | None] = mapped_column(ForeignKey("transactions.id"), nullable=True, index=True)
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    wallet_address: Mapped[str | None] = mapped_column(String(128), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)

    customer = relationship("Customer")
    transaction = relationship("Transaction")
