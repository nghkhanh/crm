import asyncio
import time

from fastapi import HTTPException
from redis import asyncio as redis_asyncio

from app.core.config import settings


class RateLimitService:
    _memory_counters: dict[str, tuple[int, float]] = {}
    _memory_lock = asyncio.Lock()

    async def enforce(self, *, bucket: str, key: str, limit: int, window_seconds: int) -> None:
        cache_key = f"ratelimit:{bucket}:{key}"
        allowed = await self._check_redis(cache_key, limit, window_seconds)
        if allowed is None:
            allowed = await self._check_memory(cache_key, limit, window_seconds)
        if not allowed:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

    async def _check_redis(self, cache_key: str, limit: int, window_seconds: int) -> bool | None:
        if not settings.redis_url:
            return None

        client = redis_asyncio.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        try:
            count = await client.incr(cache_key)
            if count == 1:
                await client.expire(cache_key, window_seconds)
            return count <= limit
        except Exception:
            return None
        finally:
            await client.aclose()

    async def _check_memory(self, cache_key: str, limit: int, window_seconds: int) -> bool:
        now = time.time()
        async with self._memory_lock:
            count, reset_at = self._memory_counters.get(cache_key, (0, now + window_seconds))
            if now >= reset_at:
                count = 0
                reset_at = now + window_seconds
            count += 1
            self._memory_counters[cache_key] = (count, reset_at)
            return count <= limit
