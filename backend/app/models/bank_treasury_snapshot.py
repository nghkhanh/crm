from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class BankTreasuryProvider(str, Enum):
    sepay = "sepay"


class BankTreasurySnapshot(TimestampMixin, Base):
    __tablename__ = "bank_treasury_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[BankTreasuryProvider] = mapped_column(
        SqlEnum(BankTreasuryProvider, name="bank_treasury_provider"),
        default=BankTreasuryProvider.sepay,
    )
    bank_account_id: Mapped[str] = mapped_column(String(64), index=True)
    account_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    account_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="VND", server_default="VND")
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    available_balance: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    status_message: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
