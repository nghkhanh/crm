from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MoneyMixin:
    @staticmethod
    def money_column(default: str = "0.00"):
        return mapped_column(Numeric(18, 2), default=Decimal(default), server_default=default)


__all__ = ["Base", "TimestampMixin", "MoneyMixin"]

