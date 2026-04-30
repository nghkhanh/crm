"""initial schema

Revision ID: 20260426_0001
Revises:
Create Date: 2026-04-26 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260426_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("admin", "cs", "accountant", name="user_role"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255)),
        sa.Column("phone", sa.String(length=50)),
        sa.Column("telegram_id", sa.String(length=100)),
        sa.Column("referral_code", sa.String(length=50)),
        sa.Column("referred_by", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("wallet_balance", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
        sa.Column("status", sa.Enum("active", "inactive", name="customer_status"), nullable=False),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_customers_email"), "customers", ["email"], unique=False)
    op.create_index(op.f("ix_customers_full_name"), "customers", ["full_name"], unique=False)
    op.create_index(op.f("ix_customers_referral_code"), "customers", ["referral_code"], unique=True)

    op.create_table(
        "ad_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("platform", sa.Enum("facebook", "tiktok", "google", name="platform_type"), nullable=False),
        sa.Column("account_id", sa.String(length=100), nullable=False),
        sa.Column("account_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "DISABLED", name="ad_account_status"), nullable=False),
        sa.Column("balance", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
        sa.Column("spend_today", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
        sa.Column("spend_7d", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
        sa.Column("spend_28d", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
        sa.Column("spend_90d", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
        sa.Column("business_license_name", sa.String(length=255)),
        sa.Column("request_id", sa.String(length=100)),
        sa.Column("team_id", sa.String(length=100)),
        sa.Column("last_synced_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_ad_accounts_account_id"), "ad_accounts", ["account_id"], unique=True)
    op.create_index(op.f("ix_ad_accounts_customer_id"), "ad_accounts", ["customer_id"], unique=False)

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("type", sa.Enum("topup_bank", "topup_usdt", "fee", "commission", "adjustment", name="transaction_type"), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("reference", sa.String(length=255)),
        sa.Column("note", sa.Text()),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_transactions_customer_id"), "transactions", ["customer_id"], unique=False)
    op.create_index(op.f("ix_transactions_reference"), "transactions", ["reference"], unique=False)

    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("total_topup", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
        sa.Column("total_fee", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
        sa.Column("total_commission", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
        sa.Column("file_url", sa.String(length=500)),
        sa.Column("status", sa.Enum("draft", "sent", "paid", name="invoice_status"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_invoices_customer_id"), "invoices", ["customer_id"], unique=False)

    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("type", sa.Enum("open_account", "support", name="ticket_type"), nullable=False),
        sa.Column("platform", sa.Enum("facebook", "tiktok", "google", name="ticket_platform"), nullable=False),
        sa.Column("status", sa.Enum("pending", "processing", "done", "rejected", name="ticket_status"), nullable=False),
        sa.Column("form_data", sa.JSON(), nullable=False),
        sa.Column("lark_ticket_id", sa.String(length=255)),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_tickets_customer_id"), "tickets", ["customer_id"], unique=False)

    op.create_table(
        "referrals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("referrer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("referee_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("commission_rate", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
        sa.Column("total_earned", sa.Numeric(18, 2), nullable=False, server_default="0.00"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_referrals_referee_id"), "referrals", ["referee_id"], unique=False)
    op.create_index(op.f("ix_referrals_referrer_id"), "referrals", ["referrer_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_referrals_referrer_id"), table_name="referrals")
    op.drop_index(op.f("ix_referrals_referee_id"), table_name="referrals")
    op.drop_table("referrals")
    op.drop_index(op.f("ix_tickets_customer_id"), table_name="tickets")
    op.drop_table("tickets")
    op.drop_index(op.f("ix_invoices_customer_id"), table_name="invoices")
    op.drop_table("invoices")
    op.drop_index(op.f("ix_transactions_reference"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_customer_id"), table_name="transactions")
    op.drop_table("transactions")
    op.drop_index(op.f("ix_ad_accounts_customer_id"), table_name="ad_accounts")
    op.drop_index(op.f("ix_ad_accounts_account_id"), table_name="ad_accounts")
    op.drop_table("ad_accounts")
    op.drop_index(op.f("ix_customers_referral_code"), table_name="customers")
    op.drop_index(op.f("ix_customers_full_name"), table_name="customers")
    op.drop_index(op.f("ix_customers_email"), table_name="customers")
    op.drop_table("customers")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
