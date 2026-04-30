from decimal import Decimal

import pytest

from app.models.customer import Customer, CustomerStatus
from app.models.customer_usdt_address import CustomerUsdtAddress, UsdtAddressNetwork, UsdtAddressStatus
from app.services.usdt import USDTService


@pytest.mark.asyncio
async def test_usdt_poll_matches_customer_deposit_address(db_session, monkeypatch):
    customer = Customer(
        full_name="Customer A",
        wallet_balance=Decimal("0.00"),
        status=CustomerStatus.active,
    )
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)

    deposit_address = CustomerUsdtAddress(
        customer_id=customer.id,
        network=UsdtAddressNetwork.trc20,
        address="T123456789012345678901234567890123",
        status=UsdtAddressStatus.active,
        assigned_at=customer.created_at,
    )
    db_session.add(deposit_address)
    await db_session.commit()
    await db_session.refresh(deposit_address)

    async def fake_get_settings_map(self):
        return {"trongrid_api_key": "test-key"}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "data": [
                    {
                        "transaction_id": "trx001",
                        "to": deposit_address.address,
                        "value": "25000000",
                    }
                ]
            }

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, url, headers=None):
            return FakeResponse()

    monkeypatch.setattr("app.services.usdt.SettingsService.get_settings_map", fake_get_settings_map)
    monkeypatch.setattr("app.services.usdt.httpx.AsyncClient", lambda timeout: FakeClient())

    payload = await USDTService(db_session).poll_transactions()
    await db_session.refresh(customer)
    await db_session.refresh(deposit_address)

    assert payload["processed"] == 1
    assert Decimal(customer.wallet_balance) == Decimal("25.00")
    assert deposit_address.last_seen_at is not None
