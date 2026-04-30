"""invoice workflow fields

Revision ID: 20260427_0008
Revises: 20260426_0007
Create Date: 2026-04-27 00:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260427_0008"
down_revision = "20260426_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("invoices", sa.Column("invoice_number", sa.String(length=50), nullable=True))
    op.add_column("invoices", sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("invoices", sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("invoices", sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f("ix_invoices_invoice_number"), "invoices", ["invoice_number"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_invoices_invoice_number"), table_name="invoices")
    op.drop_column("invoices", "locked_at")
    op.drop_column("invoices", "paid_at")
    op.drop_column("invoices", "sent_at")
    op.drop_column("invoices", "invoice_number")
