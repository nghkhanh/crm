"""treasury and wallet ops

Revision ID: 20260504_0014
Revises: 20260430_0013
Create Date: 2026-05-04 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260504_0014"
down_revision: Union[str, None] = "20260430_0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


bank_treasury_provider = sa.Enum("sepay", name="bank_treasury_provider")
usdt_wallet_inventory_network = sa.Enum("trc20", name="usdt_wallet_inventory_network")
usdt_wallet_inventory_status = sa.Enum("available", "assigned", "disabled", name="usdt_wallet_inventory_status")
usdt_wallet_gas_status = sa.Enum("unknown", "ok", "low", "missing", name="usdt_wallet_gas_status")
usdt_wallet_sweep_status = sa.Enum("idle", "ready", "pending", "completed", "failed", name="usdt_wallet_sweep_status")


def upgrade() -> None:
    bind = op.get_bind()
    bank_treasury_provider.create(bind, checkfirst=True)
    usdt_wallet_inventory_network.create(bind, checkfirst=True)
    usdt_wallet_inventory_status.create(bind, checkfirst=True)
    usdt_wallet_gas_status.create(bind, checkfirst=True)
    usdt_wallet_sweep_status.create(bind, checkfirst=True)

    op.create_table(
        "bank_treasury_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider", postgresql.ENUM("sepay", name="bank_treasury_provider", create_type=False), nullable=False),
        sa.Column("bank_account_id", sa.String(length=64), nullable=False),
        sa.Column("account_number", sa.String(length=64), nullable=True),
        sa.Column("account_name", sa.String(length=255), nullable=True),
        sa.Column("currency", sa.String(length=10), server_default="VND", nullable=False),
        sa.Column("balance", sa.Numeric(18, 2), server_default="0.00", nullable=False),
        sa.Column("available_balance", sa.Numeric(18, 2), nullable=True),
        sa.Column("status_message", sa.String(length=255), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bank_treasury_snapshots_bank_account_id"), "bank_treasury_snapshots", ["bank_account_id"], unique=False)

    op.create_table(
        "usdt_wallet_inventory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("network", postgresql.ENUM("trc20", name="usdt_wallet_inventory_network", create_type=False), nullable=False),
        sa.Column("address", sa.String(length=128), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("status", postgresql.ENUM("available", "assigned", "disabled", name="usdt_wallet_inventory_status", create_type=False), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("customer_usdt_address_id", sa.Integer(), nullable=True),
        sa.Column("trx_balance", sa.Numeric(18, 6), server_default="0.000000", nullable=False),
        sa.Column("usdt_balance", sa.Numeric(18, 6), server_default="0.000000", nullable=False),
        sa.Column("gas_status", postgresql.ENUM("unknown", "ok", "low", "missing", name="usdt_wallet_gas_status", create_type=False), nullable=False),
        sa.Column("sweep_status", postgresql.ENUM("idle", "ready", "pending", "completed", "failed", name="usdt_wallet_sweep_status", create_type=False), nullable=False),
        sa.Column("sweep_destination", sa.String(length=128), nullable=True),
        sa.Column("last_sweep_tx_id", sa.String(length=128), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_balance_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("requested_sweep_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sweep_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["customer_usdt_address_id"], ["customer_usdt_addresses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_usdt_wallet_inventory_address"), "usdt_wallet_inventory", ["address"], unique=True)
    op.create_index(op.f("ix_usdt_wallet_inventory_customer_id"), "usdt_wallet_inventory", ["customer_id"], unique=False)
    op.create_index(op.f("ix_usdt_wallet_inventory_customer_usdt_address_id"), "usdt_wallet_inventory", ["customer_usdt_address_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_usdt_wallet_inventory_customer_usdt_address_id"), table_name="usdt_wallet_inventory")
    op.drop_index(op.f("ix_usdt_wallet_inventory_customer_id"), table_name="usdt_wallet_inventory")
    op.drop_index(op.f("ix_usdt_wallet_inventory_address"), table_name="usdt_wallet_inventory")
    op.drop_table("usdt_wallet_inventory")

    op.drop_index(op.f("ix_bank_treasury_snapshots_bank_account_id"), table_name="bank_treasury_snapshots")
    op.drop_table("bank_treasury_snapshots")

    bind = op.get_bind()
    usdt_wallet_sweep_status.drop(bind, checkfirst=True)
    usdt_wallet_gas_status.drop(bind, checkfirst=True)
    usdt_wallet_inventory_status.drop(bind, checkfirst=True)
    usdt_wallet_inventory_network.drop(bind, checkfirst=True)
    bank_treasury_provider.drop(bind, checkfirst=True)
