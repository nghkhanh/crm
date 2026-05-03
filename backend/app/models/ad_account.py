from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


def enum_values(enum_cls: type[Enum]) -> list[str]:
    return [member.value for member in enum_cls]


class Platform(str, Enum):
    facebook = "facebook"
    tiktok = "tiktok"
    google = "google"


class AdSpendProvider(str, Enum):
    facebook_graph = "facebook_graph"
    smit = "smit"


class AdAccountStatus(str, Enum):
    active = "ACTIVE"
    disabled = "DISABLED"


class FacebookPaymentStatus(str, Enum):
    healthy = "healthy"
    due = "due"
    overdue = "overdue"


class AdAccount(TimestampMixin, Base):
    __tablename__ = "ad_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    platform: Mapped[Platform] = mapped_column(
        SqlEnum(Platform, name="platform_type", values_callable=enum_values),
        default=Platform.facebook,
    )
    account_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    account_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[AdAccountStatus] = mapped_column(
        SqlEnum(AdAccountStatus, name="ad_account_status", values_callable=enum_values),
        default=AdAccountStatus.active,
    )
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    spend_today: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    spend_7d: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    spend_28d: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    spend_90d: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    business_license_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    team_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    spend_provider: Mapped[AdSpendProvider] = mapped_column(
        SqlEnum(AdSpendProvider, name="ad_spend_provider", values_callable=enum_values),
        default=AdSpendProvider.facebook_graph,
        server_default=AdSpendProvider.facebook_graph.value,
    )
    amount_due: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    prepaid_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    payment_threshold: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    payment_status: Mapped[FacebookPaymentStatus] = mapped_column(
        SqlEnum(FacebookPaymentStatus, name="facebook_payment_status", values_callable=enum_values),
        default=FacebookPaymentStatus.healthy,
        server_default=FacebookPaymentStatus.healthy.value,
    )
    last_payment_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer = relationship("Customer", back_populates="ad_accounts")
