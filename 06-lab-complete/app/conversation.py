"""Conversation history stored in Redis."""
import json
from datetime import datetime, timezone

from app.config import settings
from app.storage import get_redis_client


def _history_key(user_id: str, conversation_id: str) -> str:
    return f"history:{user_id}:{conversation_id}"


def append_message(user_id: str, conversation_id: str, role: str, content: str) -> None:
    client = get_redis_client()
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    key = _history_key(user_id, conversation_id)
    pipeline = client.pipeline()
    pipeline.rpush(key, json.dumps(message, ensure_ascii=False))
    pipeline.ltrim(key, -settings.max_history_messages, -1)
    pipeline.expire(key, settings.conversation_ttl_seconds)
    pipeline.execute()


def get_history(user_id: str, conversation_id: str) -> list[dict]:
    client = get_redis_client()
    raw_messages = client.lrange(_history_key(user_id, conversation_id), 0, -1)
    history: list[dict] = []
    for raw_message in raw_messages:
        try:
            history.append(json.loads(raw_message))
        except json.JSONDecodeError:
            continue
    return history


def conversation_exists(user_id: str, conversation_id: str) -> bool:
    return bool(get_history(user_id, conversation_id))