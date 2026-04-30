from fastapi import APIRouter

from app.api.routes import (
    ad_accounts,
    auth,
    customers,
    dashboard,
    integrations,
    invoices,
    ops,
    referrals,
    settings,
    tickets,
    transactions,
    webhooks,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(ops.router, prefix="/ops", tags=["ops"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(ad_accounts.router, prefix="/ad-accounts", tags=["ad-accounts"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(referrals.router, prefix="/referrals", tags=["referrals"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
