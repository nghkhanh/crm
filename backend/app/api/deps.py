from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import Permission, User, UserRole
from app.services.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc
    user = await AuthService(session).get_user_by_id(int(user_id))
    if not user:
        raise credentials_exception
    return user


def require_roles(*roles: UserRole):
    async def role_dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return role_dependency


def require_permissions(*permissions: Permission):
    async def permission_dependency(user: User = Depends(get_current_user)) -> User:
        missing = [permission.value for permission in permissions if not user.has_permission(permission)]
        if missing:
            raise HTTPException(status_code=403, detail=f"Missing permissions: {', '.join(missing)}")
        return user

    return permission_dependency
