from decimal import Decimal
from enum import Enum

from sqlalchemy import Enum as SqlEnum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CustomerStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    telegram_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    referral_code: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    referred_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    wallet_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    status: Mapped[CustomerStatus] = mapped_column(SqlEnum(CustomerStatus, name="customer_status"), default=CustomerStatus.active)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    referrer = relationship("User", back_populates="created_customers")
    ad_accounts = relationship("AdAccount", back_populates="customer", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="customer", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="customer", cascade="all, delete-orphan")
    usdt_addresses = relationship("CustomerUsdtAddress", back_populates="customer", cascade="all, delete-orphan")
    referral_sources = relationship("Referral", foreign_keys="Referral.referrer_id", back_populates="referrer")
    referral_targets = relationship("Referral", foreign_keys="Referral.referee_id", back_populates="referee")
