from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.models.customer import Customer, CustomerStatus
from app.models.payment_reconciliation import PaymentReconciliation, ReconciliationStatus
from app.services.sepay import SePayService


@pytest.mark.asyncio
async def test_sepay_unmatched_creates_reconciliation_record(db_session):
    service = SePayService(db_session)
    matched = await service.process_webhook("UNKNOWN", Decimal("100.00"), "Topup")
    total_records = await db_session.scalar(select(func.count(PaymentReconciliation.id)))
    status = await db_session.scalar(select(PaymentReconciliation.status))

    assert matched is False
    assert total_records == 1
    assert status == ReconciliationStatus.unmatched


@pytest.mark.asyncio
async def test_sepay_credited_creates_reconciliation_record(db_session):
    customer = Customer(
        full_name="Customer A",
        referral_code="CUS001",
        wallet_balance=Decimal("0.00"),
        status=CustomerStatus.active,
    )
    db_session.add(customer)
    await db_session.commit()

    service = SePayService(db_session)
    matched = await service.process_webhook("CUS001", Decimal("100.00"), "Topup")
    total_records = await db_session.scalar(select(func.count(PaymentReconciliation.id)))
    status = await db_session.scalar(select(PaymentReconciliation.status))

    assert matched is True
    assert total_records == 1
    assert status == ReconciliationStatus.credited
