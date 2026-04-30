from fastapi.responses import HTMLResponse

import pytest

from app.api.routes.webhooks import lark_ticket_action
from app.core.security import create_lark_action_token
from app.models.ad_account import Platform
from app.models.customer import Customer, CustomerStatus
from app.models.ticket import Ticket, TicketStatus, TicketType


@pytest.mark.asyncio
async def test_lark_accept_action_updates_ticket_status(db_session):
    customer = Customer(full_name="Customer A", wallet_balance="0.00", status=CustomerStatus.active)
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)

    ticket = Ticket(
        customer_id=customer.id,
        type=TicketType.support,
        platform=Platform.facebook,
        status=TicketStatus.pending,
        form_data={},
        note="Need review",
    )
    db_session.add(ticket)
    await db_session.commit()
    await db_session.refresh(ticket)

    response = await lark_ticket_action(token=create_lark_action_token(ticket.id, "accept"), session=db_session)
    await db_session.refresh(ticket)

    assert isinstance(response, HTMLResponse)
    assert ticket.status == TicketStatus.processing


@pytest.mark.asyncio
async def test_lark_done_action_updates_ticket_status(db_session):
    customer = Customer(full_name="Customer B", wallet_balance="0.00", status=CustomerStatus.active)
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)

    ticket = Ticket(
        customer_id=customer.id,
        type=TicketType.open_account,
        platform=Platform.facebook,
        status=TicketStatus.processing,
        form_data={},
        note="Done",
    )
    db_session.add(ticket)
    await db_session.commit()
    await db_session.refresh(ticket)

    response = await lark_ticket_action(token=create_lark_action_token(ticket.id, "done"), session=db_session)
    await db_session.refresh(ticket)

    assert isinstance(response, HTMLResponse)
    assert ticket.status == TicketStatus.done
