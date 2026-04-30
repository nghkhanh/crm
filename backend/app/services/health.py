from datetime import datetime, timezone

from redis import asyncio as redis_asyncio
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.jobs.scheduler import scheduler_service
from app.schemas.health import HealthComponent, HealthStatusResponse


class HealthService:
    async def check_liveness(self) -> HealthStatusResponse:
        components = [
            HealthComponent(name="api", status="ok", detail="Application process is running"),
            HealthComponent(
                name="scheduler",
                status="ok" if scheduler_service.scheduler.running else "error",
                detail="Scheduler is running" if scheduler_service.scheduler.running else "Scheduler is not running",
            ),
        ]
        return self._build_response(components)

    async def check_readiness(self) -> HealthStatusResponse:
        components = [
            await self._check_database(),
            await self._check_redis(),
            self._check_scheduler(),
        ]
        return self._build_response(components)

    async def _check_database(self) -> HealthComponent:
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return HealthComponent(name="database", status="ok", detail="Database connection successful")
        except Exception as exc:
            return HealthComponent(name="database", status="error", detail=f"Database unavailable: {exc}")

    async def _check_redis(self) -> HealthComponent:
        if not settings.redis_url:
            return HealthComponent(name="redis", status="ok", detail="Redis disabled")

        client = redis_asyncio.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        try:
            await client.ping()
            return HealthComponent(name="redis", status="ok", detail="Redis connection successful")
        except Exception as exc:
            return HealthComponent(name="redis", status="error", detail=f"Redis unavailable: {exc}")
        finally:
            await client.aclose()

    def _check_scheduler(self) -> HealthComponent:
        if scheduler_service.scheduler.running:
            return HealthComponent(name="scheduler", status="ok", detail="Scheduler is running")
        return HealthComponent(name="scheduler", status="error", detail="Scheduler is not running")

    def _build_response(self, components: list[HealthComponent]) -> HealthStatusResponse:
        overall = "ok" if all(component.status == "ok" for component in components) else "degraded"
        return HealthStatusResponse(
            status=overall,
            timestamp=datetime.now(timezone.utc),
            components=components,
        )
