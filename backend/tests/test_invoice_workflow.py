from datetime import date
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.api.routes.invoices import generate_invoice, update_invoice_status
from app.core.security import get_password_hash
from app.models.customer import Customer, CustomerStatus
from app.models.invoice import InvoiceStatus
from app.models.transaction import Transaction, TransactionType
from app.models.user import User, UserRole
from app.schemas.invoice import InvoiceGenerateRequest, InvoiceStatusUpdate


@pytest.mark.asyncio
async def test_generate_invoice_sets_number_and_file_url(db_session):
    user = User(email="acc@example.com", password_hash=get_password_hash("secret123"), full_name="Accountant", role=UserRole.accountant)
    customer = Customer(full_name="Customer A", wallet_balance=Decimal("100.00"), status=CustomerStatus.active)
    db_session.add_all([user, customer])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(customer)

    tx = Transaction(customer_id=customer.id, type=TransactionType.topup_bank, amount=Decimal("100.00"), reference="REF1", note=None, created_by=user.id)
    db_session.add(tx)
    await db_session.commit()

    invoice = await generate_invoice(
        payload=InvoiceGenerateRequest(customer_id=customer.id, period_start=date.today(), period_end=date.today()),
        session=db_session,
        user=user,
    )

    assert invoice.invoice_number is not None
    assert invoice.file_url == f"/api/invoices/{invoice.id}/export"


@pytest.mark.asyncio
async def test_invoice_status_workflow_locks_when_paid(db_session):
    user = User(email="acc2@example.com", password_hash=get_password_hash("secret123"), full_name="Accountant", role=UserRole.accountant)
    customer = Customer(full_name="Customer B", wallet_balance=Decimal("100.00"), status=CustomerStatus.active)
    db_session.add_all([user, customer])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(customer)

    tx = Transaction(customer_id=customer.id, type=TransactionType.topup_bank, amount=Decimal("100.00"), reference="REF2", note=None, created_by=user.id)
    db_session.add(tx)
    await db_session.commit()

    invoice = await generate_invoice(
        payload=InvoiceGenerateRequest(customer_id=customer.id, period_start=date.today(), period_end=date.today()),
        session=db_session,
        user=user,
    )

    sent = await update_invoice_status(
        invoice_id=invoice.id,
        payload=InvoiceStatusUpdate(status=InvoiceStatus.sent, file_url=invoice.file_url),
        session=db_session,
        user=user,
    )
    assert sent.sent_at is not None

    paid = await update_invoice_status(
        invoice_id=invoice.id,
        payload=InvoiceStatusUpdate(status=InvoiceStatus.paid, file_url=invoice.file_url),
        session=db_session,
        user=user,
    )
    assert paid.paid_at is not None
    assert paid.locked_at is not None

    with pytest.raises(HTTPException) as exc:
        await update_invoice_status(
            invoice_id=invoice.id,
            payload=InvoiceStatusUpdate(status=InvoiceStatus.sent, file_url=invoice.file_url),
            session=db_session,
            user=user,
        )

    assert exc.value.status_code == 400
