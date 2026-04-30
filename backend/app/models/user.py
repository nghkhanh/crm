from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class UserRole(str, Enum):
    admin = "admin"
    cs = "cs"
    accountant = "accountant"
    sub_admin = "sub_admin"


class UserStatus(str, Enum):
    enabled = "enabled"
    disabled = "disabled"


class Permission(str, Enum):
    dashboard_read = "dashboard.read"
    customer_read = "customer.read"
    customer_write = "customer.write"
    customer_delete = "customer.delete"
    ad_account_read = "ad_account.read"
    ad_account_write = "ad_account.write"
    ad_account_sync = "ad_account.sync"
    transaction_read = "transaction.read"
    transaction_write = "transaction.write"
    invoice_read = "invoice.read"
    invoice_write = "invoice.write"
    ticket_read = "ticket.read"
    ticket_write = "ticket.write"
    ticket_push_lark = "ticket.push_lark"
    referral_read = "referral.read"
    referral_write = "referral.write"
    settings_read = "settings.read"
    settings_write = "settings.write"
    integration_read = "integration.read"
    audit_read = "audit.read"
    user_manage = "user.manage"


ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.admin: set(Permission),
    UserRole.sub_admin: set(Permission),
    UserRole.cs: {
        Permission.dashboard_read,
        Permission.customer_read,
        Permission.customer_write,
        Permission.ad_account_read,
        Permission.ad_account_write,
        Permission.ticket_read,
        Permission.ticket_write,
        Permission.ticket_push_lark,
    },
    UserRole.accountant: {
        Permission.dashboard_read,
        Permission.customer_read,
        Permission.transaction_read,
        Permission.transaction_write,
        Permission.invoice_read,
        Permission.invoice_write,
        Permission.referral_read,
        Permission.referral_write,
    },
}


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole, name="user_role"), default=UserRole.cs)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    team_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[UserStatus] = mapped_column(SqlEnum(UserStatus, name="user_status"), default=UserStatus.enabled, server_default="enabled")
    failed_login_attempts: Mapped[int] = mapped_column(default=0, server_default="0")
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_customers = relationship("Customer", back_populates="referrer")
    transactions = relationship("Transaction", back_populates="creator")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    assigned_tickets = relationship("Ticket", back_populates="assignee")

    def has_permission(self, permission: Permission) -> bool:
        return permission in ROLE_PERMISSIONS.get(self.role, set())
