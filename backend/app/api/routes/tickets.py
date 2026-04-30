from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_session, require_permissions
from app.models.customer import Customer
from app.models.ticket import Ticket, TicketStatus, TicketType
from app.models.user import Permission, User
from app.schemas.common import MessageResponse
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.schemas.ticket_timeline import TicketTimelineEntry
from app.services.audit import write_audit_log
from app.services.lark import LarkService
from app.models.audit_log import AuditLog

router = APIRouter()


@router.get("", response_model=list[TicketResponse], dependencies=[Depends(require_permissions(Permission.ticket_read))])
async def list_tickets(
    status: TicketStatus | None = None,
    type: TicketType | None = None,
    assigned_to: int | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[TicketResponse]:
    query = select(Ticket).options(selectinload(Ticket.assignee))
    if status:
        query = query.where(Ticket.status == status)
    if type:
        query = query.where(Ticket.type == type)
    if assigned_to:
        query = query.where(Ticket.assigned_to == assigned_to)
    result = await session.execute(query.order_by(Ticket.created_at.desc()))
    return [TicketResponse.model_validate(item) for item in result.scalars().all()]


@router.post("", response_model=TicketResponse, dependencies=[Depends(require_permissions(Permission.ticket_write))])
async def create_ticket(
    payload: TicketCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> TicketResponse:
    customer = await session.get(Customer, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if payload.assigned_to is not None:
        assignee = await session.get(User, payload.assigned_to)
        if not assignee:
            raise HTTPException(status_code=404, detail="Assigned user not found")
    ticket = Ticket(**payload.model_dump())
    session.add(ticket)
    await session.flush()
    await write_audit_log(
        session,
        user_id=user.id,
        action="ticket.create",
        entity_type="ticket",
        entity_id=ticket.id,
        metadata_json={
            "customer_id": ticket.customer_id,
            "type": ticket.type.value,
            "status": ticket.status.value,
            "assigned_to": ticket.assigned_to,
            "priority": ticket.priority.value,
        },
    )
    await session.commit()
    await session.refresh(ticket)
    await session.refresh(ticket, attribute_names=["assignee"])
    return TicketResponse.model_validate(ticket)


@router.get("/{ticket_id}", response_model=TicketResponse, dependencies=[Depends(require_permissions(Permission.ticket_read))])
async def get_ticket(ticket_id: int, session: AsyncSession = Depends(get_session)) -> TicketResponse:
    result = await session.execute(select(Ticket).where(Ticket.id == ticket_id).options(selectinload(Ticket.assignee)))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketResponse.model_validate(item)


@router.get("/{ticket_id}/timeline", response_model=list[TicketTimelineEntry], dependencies=[Depends(require_permissions(Permission.ticket_read))])
async def get_ticket_timeline(ticket_id: int, session: AsyncSession = Depends(get_session)) -> list[TicketTimelineEntry]:
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    result = await session.execute(
        select(AuditLog)
        .where(AuditLog.entity_type == "ticket", AuditLog.entity_id == str(ticket_id))
        .options(selectinload(AuditLog.user))
        .order_by(AuditLog.created_at.desc())
    )
    return [
        TicketTimelineEntry.model_validate(item).model_copy(update={"user_name": item.user.full_name if item.user else None})
        for item in result.scalars().all()
    ]


@router.patch("/{ticket_id}", response_model=TicketResponse, dependencies=[Depends(require_permissions(Permission.ticket_write))])
async def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> TicketResponse:
    item = await session.get(Ticket, ticket_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ticket not found")
    changes = payload.model_dump(exclude_unset=True)
    if "assigned_to" in changes and changes["assigned_to"] is not None:
        assignee = await session.get(User, changes["assigned_to"])
        if not assignee:
            raise HTTPException(status_code=404, detail="Assigned user not found")
    for key, value in changes.items():
        setattr(item, key, value)
    await write_audit_log(
        session,
        user_id=user.id,
        action="ticket.update",
        entity_type="ticket",
        entity_id=item.id,
        metadata_json={"changed_fields": list(changes.keys()), "status": item.status.value, "assigned_to": item.assigned_to, "priority": item.priority.value},
    )
    await session.commit()
    await session.refresh(item)
    await session.refresh(item, attribute_names=["assignee"])
    return TicketResponse.model_validate(item)


@router.post("/{ticket_id}/push-lark", response_model=MessageResponse, dependencies=[Depends(require_permissions(Permission.ticket_push_lark))])
async def push_ticket_to_lark(
    ticket_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    result = await session.execute(
        select(Ticket).where(Ticket.id == ticket_id).options(selectinload(Ticket.customer))
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    customer = await session.get(Customer, ticket.customer_id)
    await LarkService(session).push_ticket(customer, ticket)
    await write_audit_log(
        session,
        user_id=user.id,
        action="ticket.push_lark",
        entity_type="ticket",
        entity_id=ticket.id,
        metadata_json={"customer_id": ticket.customer_id},
    )
    await session.commit()
    return MessageResponse(message="Ticket pushed to Lark")
