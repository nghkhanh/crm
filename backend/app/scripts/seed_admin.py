from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole


async def seed_admin_user() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == settings.default_admin_email))
        existing = result.scalar_one_or_none()
        if existing:
            existing.password_hash = get_password_hash(settings.default_admin_password)
            existing.full_name = "Quản trị mặc định"
            existing.role = UserRole.admin
            await session.commit()
            return

        session.add(
            User(
                email=settings.default_admin_email,
                password_hash=get_password_hash(settings.default_admin_password),
                full_name="Quản trị mặc định",
                role=UserRole.admin,
            )
        )
        await session.commit()
