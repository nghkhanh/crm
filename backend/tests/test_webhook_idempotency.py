from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.models.customer import Customer, CustomerStatus
from app.models.transaction import Transaction
from app.services.sepay import SePayService


@pytest.mark.asyncio
async def test_sepay_duplicate_webhook_is_idempotent(db_session):
    customer = Customer(
        full_name="Customer A",
        referral_code="CUS001",
        wallet_balance=Decimal("0.00"),
        status=CustomerStatus.active,
    )
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)

    service = SePayService(db_session)

    first = await service.process_webhook("CUS001", Decimal("100.00"), "Topup")
    await db_session.refresh(customer)
    second = await service.process_webhook("CUS001", Decimal("100.00"), "Topup")
    await db_session.refresh(customer)

    total_transactions = await db_session.scalar(select(func.count(Transaction.id)))

    assert first is True
    assert second is True
    assert Decimal(customer.wallet_balance) == Decimal("100.00")
    assert total_transactions == 1
