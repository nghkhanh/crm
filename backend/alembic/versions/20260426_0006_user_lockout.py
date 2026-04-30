"""user lockout columns

Revision ID: 20260426_0006
Revises: 20260426_0005
Create Date: 2026-04-26 23:45:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260426_0006"
down_revision = "20260426_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("failed_login_attempts", sa.Integer(), server_default="0", nullable=False))
    op.add_column("users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_attempts")
