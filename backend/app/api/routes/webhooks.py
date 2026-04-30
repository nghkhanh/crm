from decimal import Decimal

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from jose import JWTError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.config import settings
from app.core.security import decode_token
from app.models.ticket import Ticket, TicketStatus
from app.schemas.common import MessageResponse
from app.services.audit import write_audit_log
from app.services.rate_limit import RateLimitService
from app.services.sepay import SePayService
from app.services.usdt import USDTService

router = APIRouter()


class SePayPayload(BaseModel):
    reference: str
    amount: Decimal
    note: str | None = None


@router.post("/sepay", response_model=MessageResponse)
async def sepay_webhook(
    payload: SePayPayload,
    request: Request,
    session: AsyncSession = Depends(get_session),
    x_sepay_signature: str | None = Header(default=None),
) -> MessageResponse:
    await RateLimitService().enforce(
        bucket="webhook_sepay",
        key=f"{request.client.host if request.client else 'unknown'}:{x_sepay_signature or 'unsigned'}",
        limit=settings.webhook_rate_limit_per_minute,
        window_seconds=60,
    )
    sepay_service = SePayService(session)
    configured_secret = await sepay_service.get_webhook_secret()
    if configured_secret and x_sepay_signature != configured_secret:
        raise HTTPException(status_code=401, detail="Invalid SePay signature")
    matched = await sepay_service.process_webhook(payload.reference, payload.amount, payload.note)
    if not matched:
        raise HTTPException(status_code=404, detail="Customer reference not found")
    return MessageResponse(message="SePay webhook processed")


@router.post("/usdt", response_model=dict)
async def usdt_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    await RateLimitService().enforce(
        bucket="webhook_usdt",
        key=request.client.host if request.client else "unknown",
        limit=settings.webhook_rate_limit_per_minute,
        window_seconds=60,
    )
    return await USDTService(session).poll_transactions()


@router.get("/lark/action", response_class=HTMLResponse)
async def lark_ticket_action(
    token: str = Query(...),
    request: Request = None,
    session: AsyncSession = Depends(get_session),
) -> HTMLResponse:
    await RateLimitService().enforce(
        bucket="webhook_lark_action",
        key=request.client.host if request and request.client else "unknown",
        limit=settings.webhook_rate_limit_per_minute,
        window_seconds=60,
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "lark_action":
            raise HTTPException(status_code=401, detail="Invalid action token")
        ticket_id = int(payload["sub"])
        action = payload.get("action")
    except (JWTError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=401, detail="Invalid action token") from exc

    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if action == "accept":
        ticket.status = TicketStatus.processing
        message = "Ticket da duoc tiep nhan va CRM da cap nhat trang thai sang Dang xu ly."
    elif action == "done":
        ticket.status = TicketStatus.done
        message = "Ticket da duoc hoan thanh va CRM da cap nhat trang thai sang Hoan tat."
    else:
        raise HTTPException(status_code=400, detail="Unsupported action")

    await write_audit_log(
        session,
        user_id=None,
        action=f"ticket.lark_{action}",
        entity_type="ticket",
        entity_id=ticket.id,
        metadata_json={"source": "lark_link", "status": ticket.status.value},
    )
    await session.commit()

    return HTMLResponse(
        f"""
        <!doctype html>
        <html lang="vi">
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>CRM Ticket Update</title>
            <style>
              body {{ font-family: Arial, sans-serif; background: #f4f7fb; color: #15233b; margin: 0; padding: 32px; }}
              .card {{ max-width: 640px; margin: 0 auto; background: white; border: 1px solid #e3eaf4; border-radius: 24px; padding: 28px; box-shadow: 0 12px 32px rgba(15,23,42,0.08); }}
              h1 {{ margin: 0 0 12px; font-size: 24px; }}
              p {{ margin: 0 0 10px; line-height: 1.6; }}
              .meta {{ color: #64748b; font-size: 14px; }}
            </style>
          </head>
          <body>
            <div class="card">
              <h1>Cap nhat thanh cong</h1>
              <p>{message}</p>
              <p class="meta">Ticket #{ticket.id} • Trang thai hien tai: {ticket.status.value}</p>
            </div>
          </body>
        </html>
        """
    )
