"""staff management fields

Revision ID: 20260427_0009
Revises: 20260427_0008
Create Date: 2026-04-27 01:25:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260427_0009"
down_revision = "20260427_0008"
branch_labels = None
depends_on = None


user_status = sa.Enum("enabled", "disabled", name="user_status")
user_role_new = sa.Enum("admin", "cs", "accountant", "sub_admin", name="user_role")


def upgrade() -> None:
    user_status.create(op.get_bind(), checkfirst=True)
    op.add_column("users", sa.Column("phone", sa.String(length=30), nullable=True))
    op.add_column("users", sa.Column("team_name", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("status", user_status, nullable=False, server_default="enabled"))
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'sub_admin'")


def downgrade() -> None:
    op.drop_column("users", "status")
    op.drop_column("users", "team_name")
    op.drop_column("users", "phone")
    user_status.drop(op.get_bind(), checkfirst=True)
