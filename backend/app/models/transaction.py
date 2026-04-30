from decimal import Decimal
from enum import Enum

from sqlalchemy import Enum as SqlEnum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class TransactionType(str, Enum):
    topup_bank = "topup_bank"
    topup_usdt = "topup_usdt"
    fee = "fee"
    commission = "commission"
    adjustment = "adjustment"


class TransactionSource(str, Enum):
    manual = "manual"
    sepay = "sepay"
    trongrid = "trongrid"


class TransactionStatus(str, Enum):
    posted = "posted"
    pending = "pending"
    failed = "failed"


class Transaction(TimestampMixin, Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    type: Mapped[TransactionType] = mapped_column(SqlEnum(TransactionType, name="transaction_type"))
    source: Mapped[TransactionSource] = mapped_column(SqlEnum(TransactionSource, name="transaction_source"), default=TransactionSource.manual, server_default="manual")
    status: Mapped[TransactionStatus] = mapped_column(SqlEnum(TransactionStatus, name="transaction_status"), default=TransactionStatus.posted, server_default="posted")
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    balance_before: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    balance_after: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    customer = relationship("Customer", back_populates="transactions")
    creator = relationship("User", back_populates="transactions")
