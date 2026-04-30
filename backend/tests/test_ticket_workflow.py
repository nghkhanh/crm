import pytest

from app.models.ad_account import Platform
from app.models.customer import Customer, CustomerStatus
from app.models.ticket import TicketPriority, TicketStatus, TicketType
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.api.routes.tickets import create_ticket, update_ticket


@pytest.mark.asyncio
async def test_ticket_can_be_assigned_and_prioritized(db_session):
    customer = Customer(full_name="Customer A", wallet_balance="0.00", status=CustomerStatus.active)
    creator = User(email="creator@example.com", password_hash=get_password_hash("secret123"), full_name="Creator", role=UserRole.cs)
    assignee = User(email="assignee@example.com", password_hash=get_password_hash("secret123"), full_name="Assignee", role=UserRole.cs)
    db_session.add_all([customer, creator, assignee])
    await db_session.commit()
    await db_session.refresh(customer)
    await db_session.refresh(creator)
    await db_session.refresh(assignee)

    ticket = await create_ticket(
        payload=TicketCreate(
            customer_id=customer.id,
            assigned_to=assignee.id,
            type=TicketType.support,
            platform=Platform.facebook,
            priority=TicketPriority.high,
            form_data={},
            note="Need handling",
        ),
        session=db_session,
        user=creator,
    )

    assert ticket.assigned_to == assignee.id
    assert ticket.priority == TicketPriority.high

    updated = await update_ticket(
        ticket_id=ticket.id,
        payload=TicketUpdate(status=TicketStatus.processing, priority=TicketPriority.urgent, assigned_to=creator.id, note="Taken over"),
        session=db_session,
        user=creator,
    )

    assert updated.status == TicketStatus.processing
    assert updated.priority == TicketPriority.urgent
    assert updated.assigned_to == creator.id
