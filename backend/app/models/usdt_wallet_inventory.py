from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.customer_usdt_address import UsdtAddressNetwork


class UsdtWalletInventoryStatus(str, Enum):
    available = "available"
    assigned = "assigned"
    disabled = "disabled"


class UsdtWalletGasStatus(str, Enum):
    unknown = "unknown"
    ok = "ok"
    low = "low"
    missing = "missing"


class UsdtWalletSweepStatus(str, Enum):
    idle = "idle"
    ready = "ready"
    pending = "pending"
    completed = "completed"
    failed = "failed"


class UsdtWalletInventory(TimestampMixin, Base):
    __tablename__ = "usdt_wallet_inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    network: Mapped[UsdtAddressNetwork] = mapped_column(
        SqlEnum(UsdtAddressNetwork, name="usdt_wallet_inventory_network"),
        default=UsdtAddressNetwork.trc20,
    )
    address: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[UsdtWalletInventoryStatus] = mapped_column(
        SqlEnum(UsdtWalletInventoryStatus, name="usdt_wallet_inventory_status"),
        default=UsdtWalletInventoryStatus.available,
    )
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True, index=True)
    customer_usdt_address_id: Mapped[int | None] = mapped_column(ForeignKey("customer_usdt_addresses.id"), nullable=True, index=True)
    trx_balance: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0.000000"), server_default="0.000000")
    usdt_balance: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0.000000"), server_default="0.000000")
    gas_status: Mapped[UsdtWalletGasStatus] = mapped_column(
        SqlEnum(UsdtWalletGasStatus, name="usdt_wallet_gas_status"),
        default=UsdtWalletGasStatus.unknown,
    )
    sweep_status: Mapped[UsdtWalletSweepStatus] = mapped_column(
        SqlEnum(UsdtWalletSweepStatus, name="usdt_wallet_sweep_status"),
        default=UsdtWalletSweepStatus.idle,
    )
    sweep_destination: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_sweep_tx_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_balance_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    requested_sweep_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sweep_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    customer = relationship("Customer")
    customer_usdt_address = relationship("CustomerUsdtAddress")
