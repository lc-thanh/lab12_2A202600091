"""Monthly cost guard backed by Redis."""
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.config import settings
from app.storage import get_redis_client


def _budget_key(user_id: str) -> str:
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    return f"budget:{user_id}:{month}"


def _seconds_until_next_month() -> int:
    now = datetime.now(timezone.utc)
    next_month = (now.replace(day=28) + timedelta(days=4)).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    return max(1, int((next_month - now).total_seconds()) + 86_400)


def estimate_cost(question: str, answer: str = "") -> float:
    input_tokens = max(1, len(question.split()) * 2)
    output_tokens = max(1, len(answer.split()) * 2)
    return round((input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006, 6)


def check_budget(user_id: str, estimated_cost: float) -> float:
    client = get_redis_client()
    key = _budget_key(user_id)
    ttl_seconds = _seconds_until_next_month()

    script = """
    local current = tonumber(redis.call('GET', KEYS[1]) or '0')
    local increment = tonumber(ARGV[1])
    local budget = tonumber(ARGV[2])
    if current + increment > budget then
        return {0, current}
    end
    local updated = redis.call('INCRBYFLOAT', KEYS[1], increment)
    redis.call('EXPIRE', KEYS[1], tonumber(ARGV[3]))
    return {1, updated}
    """

    approved, current_spend = client.eval(
        script,
        1,
        key,
        float(estimated_cost),
        float(settings.monthly_budget_usd),
        int(ttl_seconds),
    )

    if int(approved) != 1:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Monthly budget exceeded for user {user_id}",
        )

    return float(current_spend)


def get_monthly_spend(user_id: str) -> float:
    client = get_redis_client()
    value = client.get(_budget_key(user_id))
    return float(value or 0.0)