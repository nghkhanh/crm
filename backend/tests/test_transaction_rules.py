from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.models.customer import Customer, CustomerStatus
from app.models.transaction import TransactionType
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.schemas.transaction import TransactionCreate
from app.api.routes.transactions import create_transaction


@pytest.mark.asyncio
async def test_transaction_updates_wallet_balance(db_session):
    user = User(email="acc@example.com", password_hash=get_password_hash("secret123"), full_name="Accountant", role=UserRole.accountant)
    customer = Customer(full_name="Customer A", wallet_balance=Decimal("100.00"), status=CustomerStatus.active)
    db_session.add_all([user, customer])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(customer)

    response = await create_transaction(
        payload=TransactionCreate(customer_id=customer.id, type=TransactionType.fee, amount=Decimal("30.00"), reference=None, note=None),
        session=db_session,
        user=user,
    )
    await db_session.refresh(customer)

    assert response.customer_id == customer.id
    assert Decimal(customer.wallet_balance) == Decimal("70.00")
    assert response.source.value == "manual"
    assert response.status.value == "posted"
    assert Decimal(response.balance_before) == Decimal("100.00")
    assert Decimal(response.balance_after) == Decimal("70.00")


@pytest.mark.asyncio
async def test_transaction_rejects_negative_wallet(db_session):
    user = User(email="acc2@example.com", password_hash=get_password_hash("secret123"), full_name="Accountant", role=UserRole.accountant)
    customer = Customer(full_name="Customer B", wallet_balance=Decimal("20.00"), status=CustomerStatus.active)
    db_session.add_all([user, customer])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(customer)

    with pytest.raises(HTTPException) as exc:
        await create_transaction(
            payload=TransactionCreate(customer_id=customer.id, type=TransactionType.fee, amount=Decimal("50.00"), reference=None, note=None),
            session=db_session,
            user=user,
        )

    assert exc.value.status_code == 400
