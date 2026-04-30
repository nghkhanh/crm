from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    return jwt.encode({"sub": subject, "exp": expire, "type": "access"}, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, jti: str | None = None) -> tuple[str, datetime, str]:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    token_jti = jti or uuid4().hex
    token = jwt.encode({"sub": subject, "exp": expire, "type": "refresh", "jti": token_jti}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expire, token_jti


def create_lark_action_token(ticket_id: int, action: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode(
        {"sub": str(ticket_id), "exp": expire, "type": "lark_action", "action": action},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
