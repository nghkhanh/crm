from decimal import Decimal
from datetime import datetime, time, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_session, require_permissions
from app.models.customer import Customer
from app.models.invoice import Invoice, InvoiceStatus
from app.models.transaction import Transaction, TransactionType
from app.models.user import Permission, User
from app.schemas.invoice import InvoiceGenerateRequest, InvoiceResponse, InvoiceStatusUpdate
from app.services.audit import write_audit_log

router = APIRouter()


@router.get("", response_model=list[InvoiceResponse], dependencies=[Depends(require_permissions(Permission.invoice_read))])
async def list_invoices(
    customer_id: int | None = None,
    status: InvoiceStatus | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[InvoiceResponse]:
    query = select(Invoice)
    if customer_id:
        query = query.where(Invoice.customer_id == customer_id)
    if status:
        query = query.where(Invoice.status == status)
    result = await session.execute(query.order_by(Invoice.created_at.desc()))
    return [InvoiceResponse.model_validate(item) for item in result.scalars().all()]


@router.post("/generate", response_model=InvoiceResponse, dependencies=[Depends(require_permissions(Permission.invoice_write))])
async def generate_invoice(
    payload: InvoiceGenerateRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> InvoiceResponse:
    if payload.period_end < payload.period_start:
        raise HTTPException(status_code=400, detail="period_end must be after period_start")
    customer = await session.get(Customer, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    existing = await session.execute(
        select(Invoice).where(
            Invoice.customer_id == payload.customer_id,
            Invoice.period_start == payload.period_start,
            Invoice.period_end == payload.period_end,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Invoice for this period already exists")
    result = await session.execute(
        select(Transaction).where(
            Transaction.customer_id == payload.customer_id,
            Transaction.created_at >= datetime.combine(payload.period_start, time.min),
            Transaction.created_at <= datetime.combine(payload.period_end, time.max),
        )
    )
    transactions = result.scalars().all()
    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions found for selected period")
    invoice = Invoice(
        customer_id=payload.customer_id,
        period_start=payload.period_start,
        period_end=payload.period_end,
        total_topup=sum((tx.amount for tx in transactions if tx.type in {TransactionType.topup_bank, TransactionType.topup_usdt}), Decimal("0.00")),
        total_fee=sum((tx.amount for tx in transactions if tx.type == TransactionType.fee), Decimal("0.00")),
        total_commission=sum((tx.amount for tx in transactions if tx.type == TransactionType.commission), Decimal("0.00")),
        status=InvoiceStatus.draft,
    )
    session.add(invoice)
    await session.flush()
    invoice.invoice_number = f"INV-{invoice.id:06d}"
    invoice.file_url = f"/api/invoices/{invoice.id}/export"
    await write_audit_log(
        session,
        user_id=user.id,
        action="invoice.generate",
        entity_type="invoice",
        entity_id=invoice.id,
        metadata_json={"customer_id": invoice.customer_id, "period_start": str(invoice.period_start), "period_end": str(invoice.period_end)},
    )
    await session.commit()
    await session.refresh(invoice)
    return InvoiceResponse.model_validate(invoice)


@router.get("/{invoice_id}", response_model=InvoiceResponse, dependencies=[Depends(require_permissions(Permission.invoice_read))])
async def get_invoice(invoice_id: int, session: AsyncSession = Depends(get_session)) -> InvoiceResponse:
    item = await session.get(Invoice, invoice_id)
    if not item:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return InvoiceResponse.model_validate(item)


@router.get("/{invoice_id}/export", response_class=HTMLResponse, dependencies=[Depends(require_permissions(Permission.invoice_read))])
async def export_invoice(invoice_id: int, session: AsyncSession = Depends(get_session)) -> HTMLResponse:
    result = await session.execute(select(Invoice, Customer).join(Customer, Customer.id == Invoice.customer_id).where(Invoice.id == invoice_id))
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice, customer = row
    return HTMLResponse(
        f"""
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>{invoice.invoice_number or f"INV-{invoice.id}"}</title>
            <style>
              body {{ font-family: Arial, sans-serif; background: #f4f7fb; color: #15233b; margin: 0; padding: 32px; }}
              .sheet {{ max-width: 860px; margin: 0 auto; background: white; border: 1px solid #e3eaf4; border-radius: 24px; padding: 32px; box-shadow: 0 12px 32px rgba(15,23,42,0.08); }}
              .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
              .block {{ border: 1px solid #e8eef7; border-radius: 16px; padding: 16px; background: #fbfdff; }}
              h1, h2, p {{ margin: 0; }}
              .muted {{ color: #64748b; }}
              .section {{ margin-top: 24px; }}
              table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
              th, td {{ padding: 12px; border-bottom: 1px solid #e8eef7; text-align: left; }}
            </style>
          </head>
          <body>
            <div class="sheet">
              <p class="muted">Vision Line CRM Invoice</p>
              <h1 style="margin-top:8px;">{invoice.invoice_number or f"INV-{invoice.id}"}</h1>
              <div class="grid section">
                <div class="block">
                  <p class="muted">Customer</p>
                  <h2 style="margin-top:8px;">{customer.full_name}</h2>
                  <p class="muted" style="margin-top:8px;">{customer.email or "-"}</p>
                </div>
                <div class="block">
                  <p class="muted">Billing Period</p>
                  <h2 style="margin-top:8px;">{invoice.period_start} to {invoice.period_end}</h2>
                  <p class="muted" style="margin-top:8px;">Status: {invoice.status.value}</p>
                </div>
              </div>
              <div class="section">
                <table>
                  <thead>
                    <tr>
                      <th>Topup</th>
                      <th>Fee</th>
                      <th>Commission</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>${invoice.total_topup}</td>
                      <td>${invoice.total_fee}</td>
                      <td>${invoice.total_commission}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </body>
        </html>
        """
    )


@router.patch("/{invoice_id}/status", response_model=InvoiceResponse, dependencies=[Depends(require_permissions(Permission.invoice_write))])
async def update_invoice_status(
    invoice_id: int,
    payload: InvoiceStatusUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> InvoiceResponse:
    item = await session.get(Invoice, invoice_id)
    if not item:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if item.locked_at and payload.status != item.status:
        raise HTTPException(status_code=400, detail="Locked invoice cannot be modified")
    current = item.status
    next_status = payload.status
    allowed = {
        InvoiceStatus.draft: {InvoiceStatus.draft, InvoiceStatus.sent},
        InvoiceStatus.sent: {InvoiceStatus.sent, InvoiceStatus.paid},
        InvoiceStatus.paid: {InvoiceStatus.paid},
    }
    if next_status not in allowed[current]:
        raise HTTPException(status_code=400, detail="Invalid invoice status transition")
    item.status = next_status
    if payload.file_url is not None:
        item.file_url = payload.file_url
    if next_status == InvoiceStatus.sent and item.sent_at is None:
        item.sent_at = datetime.now(timezone.utc)
    if next_status == InvoiceStatus.paid:
        if item.sent_at is None:
            item.sent_at = datetime.now(timezone.utc)
        if item.paid_at is None:
            item.paid_at = datetime.now(timezone.utc)
        if item.locked_at is None:
            item.locked_at = datetime.now(timezone.utc)
    await write_audit_log(
        session,
        user_id=user.id,
        action="invoice.status_update",
        entity_type="invoice",
        entity_id=item.id,
        metadata_json={"from_status": current.value, "status": item.status.value, "file_url": item.file_url},
    )
    await session.commit()
    await session.refresh(item)
    return InvoiceResponse.model_validate(item)
