"""ticket assignment and priority

Revision ID: 20260426_0007
Revises: 20260426_0006
Create Date: 2026-04-26 23:58:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260426_0007"
down_revision = "20260426_0006"
branch_labels = None
depends_on = None


ticket_priority = sa.Enum("low", "normal", "high", "urgent", name="ticket_priority")


def upgrade() -> None:
    ticket_priority.create(op.get_bind(), checkfirst=True)
    op.add_column("tickets", sa.Column("assigned_to", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("tickets", sa.Column("priority", ticket_priority, nullable=False, server_default="normal"))
    op.create_index(op.f("ix_tickets_assigned_to"), "tickets", ["assigned_to"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tickets_assigned_to"), table_name="tickets")
    op.drop_column("tickets", "priority")
    op.drop_column("tickets", "assigned_to")
    ticket_priority.drop(op.get_bind(), checkfirst=True)
