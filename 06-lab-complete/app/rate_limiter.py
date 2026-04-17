"""Sliding-window rate limiting backed by Redis."""
import time
import uuid

from fastapi import HTTPException, status

from app.config import settings
from app.storage import get_redis_client


def _rate_limit_key(user_id: str) -> str:
    return f"rate_limit:{user_id}"


def check_rate_limit(user_id: str) -> None:
    client = get_redis_client()
    key = _rate_limit_key(user_id)
    now_ms = int(time.time() * 1000)
    window_start = now_ms - 60_000

    pipeline = client.pipeline()
    pipeline.zremrangebyscore(key, 0, window_start)
    pipeline.zcard(key)
    _, request_count = pipeline.execute()

    if request_count >= settings.rate_limit_per_minute:
        oldest = client.zrange(key, 0, 0, withscores=True)
        retry_after = 60
        if oldest:
            oldest_ts = int(oldest[0][1])
            retry_after = max(1, 60 - int((now_ms - oldest_ts) / 1000))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
            headers={"Retry-After": str(retry_after)},
        )

    member = f"{now_ms}:{uuid.uuid4().hex}"
    client.zadd(key, {member: now_ms})
    client.expire(key, 120)