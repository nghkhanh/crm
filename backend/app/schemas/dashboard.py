from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_customers: int
    total_wallet_balance: float
    total_spend_today: float
    active_accounts_count: int
    disabled_accounts_count: int
    block_rate_quarter: float
    block_rate_90d: float
    pending_tickets_count: int
    spend_trend_7d: list[dict]
    spend_trend_28d: list[dict]
