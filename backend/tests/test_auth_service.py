import pytest

from app.core.config import settings
from app.core.security import decode_token, get_password_hash
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest
from app.services.auth import AuthService


@pytest.mark.asyncio
async def test_login_and_refresh_rotation(db_session):
    user = User(
        email="admin@example.com",
        password_hash=get_password_hash("secret123"),
        full_name="Admin",
        role=UserRole.admin,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    service = AuthService(db_session)
    tokens = await service.login(LoginRequest(email="admin@example.com", password="secret123"))
    refresh_payload = decode_token(tokens.refresh_token)
    rotated = await service.refresh(user, refresh_payload["jti"])
    rotated_payload = decode_token(rotated.refresh_token)

    assert tokens.access_token
    assert rotated.access_token
    assert refresh_payload["jti"] != rotated_payload["jti"]


@pytest.mark.asyncio
async def test_revoked_refresh_token_cannot_be_reused(db_session):
    user = User(
        email="revoke@example.com",
        password_hash=get_password_hash("secret123"),
        full_name="Admin",
        role=UserRole.admin,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    service = AuthService(db_session)
    tokens = await service.login(LoginRequest(email="revoke@example.com", password="secret123"))
    refresh_payload = decode_token(tokens.refresh_token)

    await service.revoke_refresh_token(user, refresh_payload["jti"])

    with pytest.raises(ValueError):
        await service.refresh(user, refresh_payload["jti"])


@pytest.mark.asyncio
async def test_failed_login_can_lock_account(db_session):
    original_attempts = settings.auth_lockout_max_attempts
    original_minutes = settings.auth_lockout_minutes
    settings.auth_lockout_max_attempts = 2
    settings.auth_lockout_minutes = 5
    try:
        user = User(
            email="locked@example.com",
            password_hash=get_password_hash("secret123"),
            full_name="Locked User",
            role=UserRole.admin,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = AuthService(db_session)

        with pytest.raises(ValueError):
            await service.login(LoginRequest(email="locked@example.com", password="wrong"))

        with pytest.raises(ValueError):
            await service.login(LoginRequest(email="locked@example.com", password="wrong-again"))

        await db_session.refresh(user)
        assert user.locked_until is not None

        with pytest.raises(PermissionError):
            await service.login(LoginRequest(email="locked@example.com", password="secret123"))
    finally:
        settings.auth_lockout_max_attempts = original_attempts
        settings.auth_lockout_minutes = original_minutes
