"""transaction ledger fields

Revision ID: 20260427_0011
Revises: 20260427_0010
Create Date: 2026-04-27 03:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260427_0011"
down_revision = "20260427_0010"
branch_labels = None
depends_on = None


transaction_source = sa.Enum("manual", "sepay", "trongrid", name="transaction_source")
transaction_status = sa.Enum("posted", "pending", "failed", name="transaction_status")


def upgrade() -> None:
    transaction_source.create(op.get_bind(), checkfirst=True)
    transaction_status.create(op.get_bind(), checkfirst=True)
    op.add_column("transactions", sa.Column("source", transaction_source, nullable=False, server_default="manual"))
    op.add_column("transactions", sa.Column("status", transaction_status, nullable=False, server_default="posted"))
    op.add_column("transactions", sa.Column("balance_before", sa.Numeric(18, 2), nullable=False, server_default="0.00"))
    op.add_column("transactions", sa.Column("balance_after", sa.Numeric(18, 2), nullable=False, server_default="0.00"))


def downgrade() -> None:
    op.drop_column("transactions", "balance_after")
    op.drop_column("transactions", "balance_before")
    op.drop_column("transactions", "status")
    op.drop_column("transactions", "source")
    transaction_status.drop(op.get_bind(), checkfirst=True)
    transaction_source.drop(op.get_bind(), checkfirst=True)
