"""payment reconciliations

Revision ID: 20260427_0012
Revises: 20260427_0011
Create Date: 2026-04-27 03:35:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260427_0012"
down_revision = "20260427_0011"
branch_labels = None
depends_on = None


reconciliation_channel = postgresql.ENUM("bank", "usdt", name="reconciliation_channel", create_type=False)
reconciliation_status = postgresql.ENUM("credited", "unmatched", "duplicate", "ignored", name="reconciliation_status", create_type=False)


def upgrade() -> None:
    postgresql.ENUM("bank", "usdt", name="reconciliation_channel").create(op.get_bind(), checkfirst=True)
    postgresql.ENUM("credited", "unmatched", "duplicate", "ignored", name="reconciliation_status").create(op.get_bind(), checkfirst=True)
    op.create_table(
        "payment_reconciliations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("channel", reconciliation_channel, nullable=False),
        sa.Column("status", reconciliation_status, nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("transaction_id", sa.Integer(), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("reference", sa.String(length=255), nullable=True),
        sa.Column("wallet_address", sa.String(length=128), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payment_reconciliations_customer_id"), "payment_reconciliations", ["customer_id"], unique=False)
    op.create_index(op.f("ix_payment_reconciliations_transaction_id"), "payment_reconciliations", ["transaction_id"], unique=False)
    op.create_index(op.f("ix_payment_reconciliations_external_id"), "payment_reconciliations", ["external_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_payment_reconciliations_external_id"), table_name="payment_reconciliations")
    op.drop_index(op.f("ix_payment_reconciliations_transaction_id"), table_name="payment_reconciliations")
    op.drop_index(op.f("ix_payment_reconciliations_customer_id"), table_name="payment_reconciliations")
    op.drop_table("payment_reconciliations")
    postgresql.ENUM("credited", "unmatched", "duplicate", "ignored", name="reconciliation_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM("bank", "usdt", name="reconciliation_channel").drop(op.get_bind(), checkfirst=True)
