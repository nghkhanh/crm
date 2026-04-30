from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_session, require_permissions
from app.models.customer import Customer, CustomerStatus
from app.models.customer_usdt_address import CustomerUsdtAddress
from app.models.user import Permission, User
from app.schemas.ad_account import AdAccountResponse
from app.schemas.customer import CustomerCreate, CustomerDetailResponse, CustomerResponse, CustomerUpdate
from app.schemas.ticket import TicketResponse
from app.schemas.transaction import TransactionResponse
from app.schemas.usdt_address import CustomerUsdtAddressCreate, CustomerUsdtAddressResponse, CustomerUsdtAddressUpdate
from app.services.audit import write_audit_log

router = APIRouter()


@router.get("", response_model=dict, dependencies=[Depends(require_permissions(Permission.customer_read))])
async def list_customers(
    page: int = Query(1, ge=1),
    search: str | None = None,
    status: CustomerStatus | None = None,
    session: AsyncSession = Depends(get_session),
):
    query = select(Customer)
    if search:
        query = query.where(or_(Customer.full_name.ilike(f"%{search}%"), Customer.email.ilike(f"%{search}%")))
    if status:
        query = query.where(Customer.status == status)
    result = await session.execute(query.order_by(Customer.created_at.desc()))
    items = result.scalars().all()
    page_size = 10
    start = (page - 1) * page_size
    sliced = items[start : start + page_size]
    return {
        "items": [CustomerResponse.model_validate(item).model_dump() for item in sliced],
        "total": len(items),
        "page": page,
        "page_size": page_size,
    }


@router.get("/{customer_id}", response_model=CustomerDetailResponse, dependencies=[Depends(require_permissions(Permission.customer_read))])
async def get_customer(customer_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Customer)
        .where(Customer.id == customer_id)
        .options(selectinload(Customer.ad_accounts), selectinload(Customer.transactions), selectinload(Customer.tickets), selectinload(Customer.usdt_addresses))
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {
        "profile": CustomerResponse.model_validate(customer).model_dump(),
        "ad_accounts": [AdAccountResponse.model_validate(account).model_dump() for account in customer.ad_accounts],
        "recent_transactions": [TransactionResponse.model_validate(tx).model_dump() for tx in customer.transactions[:10]],
        "tickets": [TicketResponse.model_validate(ticket).model_dump() for ticket in customer.tickets],
        "usdt_addresses": [CustomerUsdtAddressResponse.model_validate(address).model_dump() for address in customer.usdt_addresses],
    }


@router.post("", response_model=CustomerResponse, dependencies=[Depends(require_permissions(Permission.customer_write))])
async def create_customer(
    payload: CustomerCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> CustomerResponse:
    customer = Customer(**payload.model_dump())
    session.add(customer)
    await session.flush()
    await write_audit_log(
        session,
        user_id=user.id,
        action="customer.create",
        entity_type="customer",
        entity_id=customer.id,
        metadata_json={"full_name": customer.full_name, "status": customer.status.value},
    )
    await session.commit()
    await session.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerResponse, dependencies=[Depends(require_permissions(Permission.customer_write))])
async def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> CustomerResponse:
    customer = await session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    changes = payload.model_dump(exclude_unset=True)
    if "wallet_balance" in changes:
        raise HTTPException(status_code=400, detail="Wallet balance must be changed through transactions")
    for key, value in changes.items():
        setattr(customer, key, value)
    await write_audit_log(
        session,
        user_id=user.id,
        action="customer.update",
        entity_type="customer",
        entity_id=customer.id,
        metadata_json={"changed_fields": list(changes.keys())},
    )
    await session.commit()
    await session.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}", response_model=dict, dependencies=[Depends(require_permissions(Permission.customer_delete))])
async def delete_customer(
    customer_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    customer = await session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    result = await session.execute(
        select(Customer)
        .where(Customer.id == customer_id)
        .options(selectinload(Customer.ad_accounts), selectinload(Customer.transactions), selectinload(Customer.tickets), selectinload(Customer.invoices))
    )
    hydrated_customer = result.scalar_one()
    if hydrated_customer.ad_accounts or hydrated_customer.transactions or hydrated_customer.tickets or hydrated_customer.invoices:
        raise HTTPException(status_code=400, detail="Customer has related operational data and cannot be deleted")
    await write_audit_log(
        session,
        user_id=user.id,
        action="customer.delete",
        entity_type="customer",
        entity_id=customer.id,
        metadata_json={"full_name": customer.full_name},
    )
    await session.delete(customer)
    await session.commit()
    return {"message": "Customer deleted"}


@router.get("/{customer_id}/usdt-addresses", response_model=list[CustomerUsdtAddressResponse], dependencies=[Depends(require_permissions(Permission.customer_read))])
async def list_customer_usdt_addresses(customer_id: int, session: AsyncSession = Depends(get_session)) -> list[CustomerUsdtAddressResponse]:
    customer = await session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    result = await session.execute(select(CustomerUsdtAddress).where(CustomerUsdtAddress.customer_id == customer_id).order_by(CustomerUsdtAddress.created_at.desc()))
    return [CustomerUsdtAddressResponse.model_validate(item) for item in result.scalars().all()]


@router.post("/{customer_id}/usdt-addresses", response_model=CustomerUsdtAddressResponse, dependencies=[Depends(require_permissions(Permission.customer_write))])
async def create_customer_usdt_address(
    customer_id: int,
    payload: CustomerUsdtAddressCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> CustomerUsdtAddressResponse:
    customer = await session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    existing = await session.scalar(select(CustomerUsdtAddress).where(CustomerUsdtAddress.address == payload.address))
    if existing:
        raise HTTPException(status_code=400, detail="USDT deposit address already assigned")
    address = CustomerUsdtAddress(
        customer_id=customer_id,
        address=payload.address,
        label=payload.label,
        network=payload.network,
        assigned_at=datetime.now(timezone.utc),
    )
    session.add(address)
    await session.flush()
    await write_audit_log(
        session,
        user_id=user.id,
        action="customer.usdt_address_create",
        entity_type="customer_usdt_address",
        entity_id=address.id,
        metadata_json={"customer_id": customer_id, "address": address.address, "network": address.network.value},
    )
    await session.commit()
    await session.refresh(address)
    return CustomerUsdtAddressResponse.model_validate(address)


@router.patch("/{customer_id}/usdt-addresses/{address_id}", response_model=CustomerUsdtAddressResponse, dependencies=[Depends(require_permissions(Permission.customer_write))])
async def update_customer_usdt_address(
    customer_id: int,
    address_id: int,
    payload: CustomerUsdtAddressUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> CustomerUsdtAddressResponse:
    address = await session.get(CustomerUsdtAddress, address_id)
    if not address or address.customer_id != customer_id:
        raise HTTPException(status_code=404, detail="USDT deposit address not found")
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(address, key, value)
    await write_audit_log(
        session,
        user_id=user.id,
        action="customer.usdt_address_update",
        entity_type="customer_usdt_address",
        entity_id=address.id,
        metadata_json={"customer_id": customer_id, "changed_fields": list(changes.keys())},
    )
    await session.commit()
    await session.refresh(address)
    return CustomerUsdtAddressResponse.model_validate(address)
