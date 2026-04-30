from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Referral(TimestampMixin, Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    referee_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    commission_rate: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")
    total_earned: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), server_default="0.00")

    referrer = relationship("Customer", foreign_keys=[referrer_id], back_populates="referral_sources")
    referee = relationship("Customer", foreign_keys=[referee_id], back_populates="referral_targets")
