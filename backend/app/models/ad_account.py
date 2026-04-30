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


class AdAccountStatus(str, Enum):
    active = "ACTIVE"
    disabled = "DISABLED"


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
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer = relationship("Customer", back_populates="ad_accounts")
