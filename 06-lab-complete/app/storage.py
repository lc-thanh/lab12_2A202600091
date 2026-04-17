"""Shared Redis client helpers."""
from functools import lru_cache
import logging

from redis import Redis, RedisError

from app.config import settings


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_redis_client() -> Redis:
    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
        health_check_interval=30,
    )


def ping_redis() -> bool:
    try:
        return bool(get_redis_client().ping())
    except RedisError as exc:
        logger.warning("redis_ping_failed", extra={"error": str(exc)})
        return False