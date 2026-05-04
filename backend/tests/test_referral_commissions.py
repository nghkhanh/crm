from decimal import Decimal

import pytest

from app.models.customer import Customer, CustomerStatus
from app.models.referral import Referral
from app.models.transaction import Transaction, TransactionType
from app.schemas.referral import ReferralCreate, ReferralUpdate
from app.services.referrals import ReferralService


@pytest.mark.asyncio
async def test_referral_recalculate_uses_referee_topups(db_session):
    referrer = Customer(full_name="Referrer", wallet_balance=Decimal("0.00"), status=CustomerStatus.active)
    referee = Customer(full_name="Referee", wallet_balance=Decimal("0.00"), status=CustomerStatus.active)
    db_session.add_all([referrer, referee])
    await db_session.commit()
    await db_session.refresh(referrer)
    await db_session.refresh(referee)

    referral = Referral(referrer_id=referrer.id, referee_id=referee.id, commission_rate=Decimal("5.00"))
    db_session.add(referral)
    db_session.add_all(
        [
            Transaction(customer_id=referee.id, type=TransactionType.topup_bank, amount=Decimal("100.00")),
            Transaction(customer_id=referee.id, type=TransactionType.topup_usdt, amount=Decimal("50.00")),
            Transaction(customer_id=referee.id, type=TransactionType.fee, amount=Decimal("20.00")),
        ]
    )
    await db_session.commit()

    payload = await ReferralService(db_session).recalculate()
    await db_session.refresh(referral)

    assert payload["updated"] == 1
    assert Decimal(referral.total_earned) == Decimal("7.50")


def test_referral_create_rejects_same_customer():
    with pytest.raises(ValueError):
        ReferralCreate(referrer_id=1, referee_id=1, commission_rate=Decimal("5.00"))


def test_referral_update_rejects_same_customer():
    with pytest.raises(ValueError):
        ReferralUpdate(referrer_id=2, referee_id=2, commission_rate=Decimal("7.00"))
