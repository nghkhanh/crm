from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserStatus
from app.schemas.auth import LoginRequest, StaffCreateRequest, StaffUpdateRequest, TokenResponse


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_refresh_token_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self.session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
        return result.scalar_one_or_none()

    async def issue_tokens(self, user: User) -> TokenResponse:
        refresh_token, expires_at, jti = create_refresh_token(str(user.id))
        self.session.add(RefreshToken(user_id=user.id, jti=jti, expires_at=expires_at))
        await self.session.commit()
        return TokenResponse(access_token=create_access_token(str(user.id)), refresh_token=refresh_token)

    async def login(self, payload: LoginRequest) -> TokenResponse:
        user = await self.get_user_by_email(payload.email)
        if not user:
            raise ValueError("Invalid credentials")
        if user.status == UserStatus.disabled:
            raise PermissionError("Account is disabled")
        if user.locked_until and self._as_utc(user.locked_until) > datetime.now(timezone.utc):
            raise PermissionError("Account is temporarily locked")
        if not verify_password(payload.password, user.password_hash):
            await self.record_failed_login(user)
            raise ValueError("Invalid credentials")
        user.failed_login_attempts = 0
        user.locked_until = None
        return await self.issue_tokens(user)

    async def refresh(self, user: User, current_jti: str) -> TokenResponse:
        token_row = await self.get_refresh_token_by_jti(current_jti)
        if not token_row or token_row.user_id != user.id or token_row.revoked_at is not None:
            raise ValueError("Invalid refresh token")
        if self._as_utc(token_row.expires_at) <= datetime.now(timezone.utc):
            raise ValueError("Refresh token expired")

        token_row.revoked_at = datetime.now(timezone.utc)
        refresh_token, expires_at, new_jti = create_refresh_token(str(user.id))
        self.session.add(RefreshToken(user_id=user.id, jti=new_jti, expires_at=expires_at))
        await self.session.commit()
        return TokenResponse(access_token=create_access_token(str(user.id)), refresh_token=refresh_token)

    async def revoke_refresh_token(self, user: User, current_jti: str) -> None:
        token_row = await self.get_refresh_token_by_jti(current_jti)
        if not token_row or token_row.user_id != user.id or token_row.revoked_at is not None:
            return
        token_row.revoked_at = datetime.now(timezone.utc)
        await self.session.commit()

    async def change_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        user.password_hash = get_password_hash(new_password)
        user.failed_login_attempts = 0
        user.locked_until = None
        await self.session.commit()

    async def admin_reset_password(self, email: str, new_password: str) -> User:
        user = await self.get_user_by_email(email)
        if not user:
            raise ValueError("User not found")
        user.password_hash = get_password_hash(new_password)
        user.failed_login_attempts = 0
        user.locked_until = None
        await self.session.commit()
        return user

    async def create_staff(self, payload: StaffCreateRequest) -> User:
        existing = await self.get_user_by_email(payload.email)
        if existing:
            raise ValueError("User already exists")
        user = User(
            email=payload.email.lower(),
            password_hash=get_password_hash(payload.password),
            full_name=payload.full_name,
            role=payload.role,
            phone=payload.phone,
            team_name=payload.team_name,
            status=payload.status,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_staff(self, user_id: int, payload: StaffUpdateRequest) -> User:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.role is not None:
            user.role = payload.role
        if payload.phone is not None:
            user.phone = payload.phone
        if payload.team_name is not None:
            user.team_name = payload.team_name
        if payload.status is not None:
            user.status = payload.status
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def record_failed_login(self, user: User) -> None:
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.auth_lockout_max_attempts:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.auth_lockout_minutes)
            user.failed_login_attempts = 0
        await self.session.commit()

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
