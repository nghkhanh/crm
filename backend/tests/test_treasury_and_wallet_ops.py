from decimal import Decimal

import pytest

from app.models.customer import Customer, CustomerStatus
from app.services.bank_treasury import BankTreasuryService
from app.services.settings import SettingsService
from app.services.usdt_wallet_ops import UsdtWalletOpsService


@pytest.mark.asyncio
async def test_wallet_auto_assign_creates_customer_deposit_address(db_session):
    customer = Customer(full_name="Customer A", wallet_balance=Decimal("0.00"), status=CustomerStatus.active)
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)

    service = UsdtWalletOpsService(db_session)
    await service.create_wallet(address="T123456789012345678901234567890123", label="Pool #1")
    wallet = await service.auto_assign_next_available_wallet(customer_id=customer.id)

    assert wallet.customer_id == customer.id
    assert wallet.customer_usdt_address_id is not None
    assert wallet.status == "assigned"


@pytest.mark.asyncio
async def test_bank_treasury_sync_creates_snapshot(db_session, monkeypatch):
    async def fake_settings_map(self):
        return {"sepay_api_token": "token", "sepay_bank_account_id": "12345"}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "data": {
                    "account_number": "1900123456",
                    "account_holder_name": "Blue Media Group",
                    "currency": "VND",
                    "balance": "125000000",
                    "available_balance": "120000000",
                    "status": "active",
                }
            }

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(SettingsService, "get_settings_map", fake_settings_map)
    monkeypatch.setattr("app.services.bank_treasury.httpx.AsyncClient", lambda timeout: FakeClient())

    snapshot = await BankTreasuryService(db_session).sync_sepay_balance()

    assert snapshot.bank_account_id == "12345"
    assert Decimal(snapshot.balance) == Decimal("125000000")
    assert snapshot.account_number == "1900123456"
