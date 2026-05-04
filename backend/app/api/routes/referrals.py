from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_session, require_permissions
from app.models.referral import Referral
from app.models.user import Permission
from app.schemas.referral import ReferralCreate, ReferralResponse, ReferralUpdate
from app.services.referrals import ReferralService

router = APIRouter()


def serialize_referral(item: Referral) -> ReferralResponse:
    return ReferralResponse.model_validate(item).model_copy(
        update={
            "referrer_name": item.referrer.full_name if item.referrer else None,
            "referee_name": item.referee.full_name if item.referee else None,
        }
    )


@router.get("", response_model=list[ReferralResponse], dependencies=[Depends(require_permissions(Permission.referral_read))])
async def list_referrals(referrer_id: int | None = None, session: AsyncSession = Depends(get_session)) -> list[ReferralResponse]:
    query = select(Referral).options(selectinload(Referral.referrer), selectinload(Referral.referee))
    if referrer_id:
        query = query.where(Referral.referrer_id == referrer_id)
    result = await session.execute(query.order_by(Referral.created_at.desc()))
    return [serialize_referral(item) for item in result.scalars().all()]


@router.post("", response_model=ReferralResponse, dependencies=[Depends(require_permissions(Permission.referral_write))])
async def create_referral(payload: ReferralCreate, session: AsyncSession = Depends(get_session)) -> ReferralResponse:
    item = Referral(**payload.model_dump())
    session.add(item)
    await session.commit()
    result = await session.execute(
        select(Referral)
        .options(selectinload(Referral.referrer), selectinload(Referral.referee))
        .where(Referral.id == item.id)
    )
    return serialize_referral(result.scalar_one())


@router.patch("/{referral_id}", response_model=ReferralResponse, dependencies=[Depends(require_permissions(Permission.referral_write))])
async def update_referral(referral_id: int, payload: ReferralUpdate, session: AsyncSession = Depends(get_session)) -> ReferralResponse:
    result = await session.execute(
        select(Referral)
        .options(selectinload(Referral.referrer), selectinload(Referral.referee))
        .where(Referral.id == referral_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy referral.")

    for field, value in payload.model_dump().items():
        setattr(item, field, value)

    await session.commit()
    await session.refresh(item)
    result = await session.execute(
        select(Referral)
        .options(selectinload(Referral.referrer), selectinload(Referral.referee))
        .where(Referral.id == referral_id)
    )
    return serialize_referral(result.scalar_one())


@router.post("/calculate", response_model=dict, dependencies=[Depends(require_permissions(Permission.referral_write))])
async def calculate_referrals(session: AsyncSession = Depends(get_session)):
    return await ReferralService(session).recalculate()
