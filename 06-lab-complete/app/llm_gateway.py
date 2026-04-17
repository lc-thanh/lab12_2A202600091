"""LLM gateway: ưu tiên OpenAI, fallback sang mock khi cần."""

from __future__ import annotations

import logging

from app.config import settings
from utils.mock_llm import ask as mock_ask

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - handled by runtime fallback
    OpenAI = None  # type: ignore[assignment]


_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if OpenAI is None:
        return None
    if not settings.openai_api_key:
        return None

    _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def ask(question: str) -> tuple[str, str]:
    """Return (answer, source) where source is openai/mock/mock_fallback."""
    if not settings.openai_api_key:
        return mock_ask(question), "mock"

    try:
        client = _get_client()
    except Exception as exc:
        logger.warning("OpenAI client init failed, fallback to mock LLM: %s", exc)
        return mock_ask(question), "mock_fallback"

    if client is None:
        logger.warning("OpenAI SDK unavailable; falling back to mock LLM")
        return mock_ask(question), "mock"

    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": question}],
            temperature=0.2,
        )
        content = (response.choices[0].message.content or "").strip()
        if not content:
            raise ValueError("OpenAI returned empty content")
        return content, "openai"
    except Exception as exc:
        logger.warning("OpenAI call failed, fallback to mock LLM: %s", exc)
        return mock_ask(question), "mock_fallback"
