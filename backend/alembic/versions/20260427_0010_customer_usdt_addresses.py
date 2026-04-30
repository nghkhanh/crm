"""customer usdt deposit addresses

Revision ID: 20260427_0010
Revises: 20260427_0009
Create Date: 2026-04-27 02:05:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260427_0010"
down_revision = "20260427_0009"
branch_labels = None
depends_on = None


usdt_address_network = postgresql.ENUM("trc20", name="usdt_address_network", create_type=False)
usdt_address_status = postgresql.ENUM("active", "inactive", name="usdt_address_status", create_type=False)


def upgrade() -> None:
    postgresql.ENUM("trc20", name="usdt_address_network").create(op.get_bind(), checkfirst=True)
    postgresql.ENUM("active", "inactive", name="usdt_address_status").create(op.get_bind(), checkfirst=True)
    op.create_table(
        "customer_usdt_addresses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("network", usdt_address_network, nullable=False, server_default="trc20"),
        sa.Column("address", sa.String(length=128), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("status", usdt_address_status, nullable=False, server_default="active"),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_customer_usdt_addresses_customer_id"), "customer_usdt_addresses", ["customer_id"], unique=False)
    op.create_index(op.f("ix_customer_usdt_addresses_address"), "customer_usdt_addresses", ["address"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_customer_usdt_addresses_address"), table_name="customer_usdt_addresses")
    op.drop_index(op.f("ix_customer_usdt_addresses_customer_id"), table_name="customer_usdt_addresses")
    op.drop_table("customer_usdt_addresses")
    postgresql.ENUM("active", "inactive", name="usdt_address_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM("trc20", name="usdt_address_network").drop(op.get_bind(), checkfirst=True)
