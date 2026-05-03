"""ad spend provider and facebook payment control

Revision ID: 20260430_0013
Revises: 20260427_0012
Create Date: 2026-04-30 10:30:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260430_0013"
down_revision = "20260427_0012"
branch_labels = None
depends_on = None


ad_spend_provider = postgresql.ENUM("facebook_graph", "smit", name="ad_spend_provider", create_type=False)
facebook_payment_status = postgresql.ENUM("healthy", "due", "overdue", name="facebook_payment_status", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM("facebook_graph", "smit", name="ad_spend_provider").create(bind, checkfirst=True)
    postgresql.ENUM("healthy", "due", "overdue", name="facebook_payment_status").create(bind, checkfirst=True)
    op.add_column(
        "ad_accounts",
        sa.Column("spend_provider", ad_spend_provider, nullable=False, server_default="facebook_graph"),
    )
    op.add_column(
        "ad_accounts",
        sa.Column("amount_due", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
    )
    op.add_column(
        "ad_accounts",
        sa.Column("prepaid_balance", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
    )
    op.add_column(
        "ad_accounts",
        sa.Column("payment_threshold", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
    )
    op.add_column(
        "ad_accounts",
        sa.Column("payment_status", facebook_payment_status, nullable=False, server_default="healthy"),
    )
    op.add_column(
        "ad_accounts",
        sa.Column("last_payment_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    bind = op.get_bind()
    op.drop_column("ad_accounts", "last_payment_at")
    op.drop_column("ad_accounts", "payment_status")
    op.drop_column("ad_accounts", "payment_threshold")
    op.drop_column("ad_accounts", "prepaid_balance")
    op.drop_column("ad_accounts", "amount_due")
    op.drop_column("ad_accounts", "spend_provider")
    postgresql.ENUM("healthy", "due", "overdue", name="facebook_payment_status").drop(bind, checkfirst=True)
    postgresql.ENUM("facebook_graph", "smit", name="ad_spend_provider").drop(bind, checkfirst=True)
