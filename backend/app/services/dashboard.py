from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad_account import AdAccount, AdAccountStatus
from app.models.customer import Customer
from app.models.ticket import Ticket, TicketStatus
from app.schemas.dashboard import DashboardSummary


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_summary(self) -> DashboardSummary:
        customer_count = await self.session.scalar(select(func.count(Customer.id))) or 0
        total_wallet_balance = await self.session.scalar(select(func.coalesce(func.sum(Customer.wallet_balance), 0))) or Decimal("0")
        total_spend_today = await self.session.scalar(select(func.coalesce(func.sum(AdAccount.spend_today), 0))) or Decimal("0")

        account_counts = await self.session.execute(
            select(
                func.sum(case((AdAccount.status == AdAccountStatus.active, 1), else_=0)),
                func.sum(case((AdAccount.status == AdAccountStatus.disabled, 1), else_=0)),
            )
        )
        active_count, disabled_count = account_counts.one()
        pending_tickets = await self.session.scalar(
            select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.pending)
        ) or 0
        now = datetime.now(timezone.utc)
        quarter_start = datetime(now.year, ((now.month - 1) // 3) * 3 + 1, 1, tzinfo=timezone.utc)
        ninety_days_ago = now - timedelta(days=90)

        quarter_counts = await self.session.execute(
            select(
                func.sum(case((AdAccount.status == AdAccountStatus.active, 1), else_=0)),
                func.sum(case((AdAccount.status == AdAccountStatus.disabled, 1), else_=0)),
            ).where(AdAccount.created_at >= quarter_start)
        )
        quarter_active, quarter_disabled = quarter_counts.one()

        ninety_day_counts = await self.session.execute(
            select(
                func.sum(case((AdAccount.status == AdAccountStatus.active, 1), else_=0)),
                func.sum(case((AdAccount.status == AdAccountStatus.disabled, 1), else_=0)),
            ).where(AdAccount.created_at >= ninety_days_ago)
        )
        ninety_active, ninety_disabled = ninety_day_counts.one()

        trend_7d = [{"date": (now - timedelta(days=i)).isoformat(), "label": f"D-{i}", "value": float(total_spend_today)} for i in range(6, -1, -1)]
        trend_28d = [{"date": (now - timedelta(days=i)).isoformat(), "label": f"D-{i}", "value": float(total_spend_today)} for i in range(27, -1, -1)]

        return DashboardSummary(
            total_customers=customer_count,
            total_wallet_balance=float(total_wallet_balance),
            total_spend_today=float(total_spend_today),
            active_accounts_count=int(active_count or 0),
            disabled_accounts_count=int(disabled_count or 0),
            block_rate_quarter=self._ratio(quarter_disabled or 0, (quarter_active or 0) + (quarter_disabled or 0)),
            block_rate_90d=self._ratio(ninety_disabled or 0, (ninety_active or 0) + (ninety_disabled or 0)),
            pending_tickets_count=pending_tickets,
            spend_trend_7d=trend_7d,
            spend_trend_28d=trend_28d,
        )

    @staticmethod
    def _ratio(disabled: int, total: int) -> float:
        if total <= 0:
            return 0.0
        return round((disabled / total) * 100, 2)
