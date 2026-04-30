from fastapi import APIRouter, Depends, HTTPException, Request
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_session, require_permissions
from app.core.config import settings
from app.core.security import decode_token
from app.models.user import Permission, User
from app.schemas.auth import (
    AdminResetPasswordRequest,
    ChangePasswordRequest,
    LoginRequest,
    StaffCreateRequest,
    StaffUpdateRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.common import MessageResponse
from app.services.audit import write_audit_log
from app.services.auth import AuthService
from app.services.rate_limit import RateLimitService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, request: Request, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    await RateLimitService().enforce(
        bucket="auth_login",
        key=f"{payload.email.lower()}:{request.client.host if request.client else 'unknown'}",
        limit=settings.auth_login_rate_limit_per_minute,
        window_seconds=60,
    )
    try:
        service = AuthService(session)
        tokens = await service.login(payload)
        user = await service.get_user_by_email(payload.email)
        if user:
            await write_audit_log(
                session,
                user_id=user.id,
                action="auth.login",
                entity_type="user",
                entity_id=user.id,
                metadata_json={"email": user.email},
            )
            await session.commit()
        return tokens
    except PermissionError as exc:
        user = await AuthService(session).get_user_by_email(payload.email)
        if user:
            await write_audit_log(
                session,
                user_id=user.id,
                action="auth.login_locked",
                entity_type="user",
                entity_id=user.id,
                metadata_json={"email": user.email},
            )
            await session.commit()
        raise HTTPException(status_code=423, detail=str(exc)) from exc
    except ValueError as exc:
        user = await AuthService(session).get_user_by_email(payload.email)
        if user:
            await write_audit_log(
                session,
                user_id=user.id,
                action="auth.login_failed",
                entity_type="user",
                entity_id=user.id,
                metadata_json={"email": user.email},
            )
            await session.commit()
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: TokenRefreshRequest, request: Request, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    await RateLimitService().enforce(
        bucket="auth_refresh",
        key=request.client.host if request.client else "unknown",
        limit=settings.auth_refresh_rate_limit_per_minute,
        window_seconds=60,
    )
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        subject = decoded["sub"]
        jti = decoded.get("jti")
        if not jti:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        user = await AuthService(session).get_user_by_id(int(subject))
        if not user:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        tokens = await AuthService(session).refresh(user, jti)
        await write_audit_log(
            session,
            user_id=user.id,
            action="auth.refresh",
            entity_type="user",
            entity_id=user.id,
            metadata_json={"email": user.email},
        )
        await session.commit()
        return tokens
    except (JWTError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc


@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: TokenRefreshRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> MessageResponse:
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("type") == "refresh" and decoded.get("jti"):
            await AuthService(session).revoke_refresh_token(user, decoded["jti"])
            await write_audit_log(
                session,
                user_id=user.id,
                action="auth.logout",
                entity_type="user",
                entity_id=user.id,
                metadata_json={"email": user.email},
            )
            await session.commit()
    except JWTError:
        pass
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(user)


@router.get("/staff", response_model=list[UserResponse], dependencies=[Depends(require_permissions(Permission.user_manage))])
async def list_staff(session: AsyncSession = Depends(get_session)) -> list[UserResponse]:
    from sqlalchemy import select

    result = await session.execute(select(User).order_by(User.full_name.asc()))
    return [UserResponse.model_validate(item) for item in result.scalars().all()]


@router.post("/staff", response_model=UserResponse, dependencies=[Depends(require_permissions(Permission.user_manage))])
async def create_staff(
    payload: StaffCreateRequest,
    admin_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    try:
        user = await AuthService(session).create_staff(payload)
        await write_audit_log(
            session,
            user_id=admin_user.id,
            action="staff.create",
            entity_type="user",
            entity_id=user.id,
            metadata_json={"email": user.email, "role": user.role.value},
        )
        await session.commit()
        return UserResponse.model_validate(user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/staff/{user_id}", response_model=UserResponse, dependencies=[Depends(require_permissions(Permission.user_manage))])
async def update_staff(
    user_id: int,
    payload: StaffUpdateRequest,
    admin_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    try:
        user = await AuthService(session).update_staff(user_id, payload)
        await write_audit_log(
            session,
            user_id=admin_user.id,
            action="staff.update",
            entity_type="user",
            entity_id=user.id,
            metadata_json={"email": user.email, "role": user.role.value, "status": user.status.value},
        )
        await session.commit()
        return UserResponse.model_validate(user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> MessageResponse:
    try:
        await AuthService(session).change_password(user, payload.current_password, payload.new_password)
        await write_audit_log(
            session,
            user_id=user.id,
            action="auth.password_changed",
            entity_type="user",
            entity_id=user.id,
            metadata_json={"email": user.email},
        )
        await session.commit()
        return MessageResponse(message="Password changed successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/admin/reset-password", response_model=MessageResponse, dependencies=[Depends(require_permissions(Permission.user_manage))])
async def admin_reset_password(
    payload: AdminResetPasswordRequest,
    admin_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> MessageResponse:
    try:
        user = await AuthService(session).admin_reset_password(payload.email, payload.new_password)
        await write_audit_log(
            session,
            user_id=admin_user.id,
            action="auth.password_reset_admin",
            entity_type="user",
            entity_id=user.id,
            metadata_json={"target_email": user.email},
        )
        await session.commit()
        return MessageResponse(message="Password reset successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
