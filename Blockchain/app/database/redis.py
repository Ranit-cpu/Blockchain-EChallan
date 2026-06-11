from typing import Any
import redis.asyncio as aioredis
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_redis_pool: aioredis.Redis | None = None
_session_pool: aioredis.Redis | None = None


async def init_redis() -> None:
    global _redis_pool, _session_pool
    _redis_pool = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=50,
    )
    _session_pool = aioredis.from_url(
        settings.redis_session_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=50,
    )
    await _redis_pool.ping()
    await _session_pool.ping()
    logger.info("Redis connections established")


async def close_redis() -> None:
    global _redis_pool, _session_pool
    if _redis_pool:
        await _redis_pool.aclose()
    if _session_pool:
        await _session_pool.aclose()
    logger.info("Redis connections closed")


def get_redis() -> aioredis.Redis:
    if _redis_pool is None:
        raise RuntimeError("Redis not initialized")
    return _redis_pool


def get_session_redis() -> aioredis.Redis:
    if _session_pool is None:
        raise RuntimeError("Session Redis not initialized")
    return _session_pool


class RedisCache:
    def __init__(self, redis: aioredis.Redis, prefix: str = "cache", ttl: int = 300) -> None:
        self.redis = redis
        self.prefix = prefix
        self.ttl = ttl

    def _key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> str | None:
        return await self.redis.get(self._key(key))

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        await self.redis.set(self._key(key), value, ex=ttl or self.ttl)

    async def delete(self, key: str) -> None:
        await self.redis.delete(self._key(key))

    async def exists(self, key: str) -> bool:
        return bool(await self.redis.exists(self._key(key)))

    async def increment(self, key: str, ttl: int | None = None) -> int:
        pipe = self.redis.pipeline()
        pipe.incr(self._key(key))
        pipe.expire(self._key(key), ttl or self.ttl)
        results = await pipe.execute()
        return results[0]