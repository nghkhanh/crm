from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class UsdtAddressNetwork(str, Enum):
    trc20 = "trc20"


class UsdtAddressStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class CustomerUsdtAddress(TimestampMixin, Base):
    __tablename__ = "customer_usdt_addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    network: Mapped[UsdtAddressNetwork] = mapped_column(SqlEnum(UsdtAddressNetwork, name="usdt_address_network"), default=UsdtAddressNetwork.trc20)
    address: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[UsdtAddressStatus] = mapped_column(SqlEnum(UsdtAddressStatus, name="usdt_address_status"), default=UsdtAddressStatus.active)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer = relationship("Customer", back_populates="usdt_addresses")
