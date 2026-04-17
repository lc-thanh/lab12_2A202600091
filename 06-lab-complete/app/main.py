"""Production AI Agent — final lab project."""
import asyncio
import json
import logging
import signal
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from threading import Lock

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.auth import verify_api_key
from app.config import settings
from app.conversation import append_message, conversation_exists, get_history
from app.cost_guard import check_budget, estimate_cost, get_monthly_spend
from app.llm_gateway import ask as llm_ask
from app.rate_limiter import check_rate_limit
from app.storage import ping_redis


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

START_TIME = time.time()
STATE = {"ready": False, "shutting_down": False}
STATE_LOCK = Lock()
ACTIVE_REQUESTS = 0
REQUEST_COUNT = 0
ERROR_COUNT = 0


def emit_event(event: str, **payload) -> None:
    record = {
        "event": event,
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    logger.info(json.dumps(record, ensure_ascii=False))


def _increment_active_requests() -> None:
    global ACTIVE_REQUESTS
    with STATE_LOCK:
        ACTIVE_REQUESTS += 1


def _decrement_active_requests() -> None:
    global ACTIVE_REQUESTS
    with STATE_LOCK:
        ACTIVE_REQUESTS = max(0, ACTIVE_REQUESTS - 1)


def _get_active_requests() -> int:
    with STATE_LOCK:
        return ACTIVE_REQUESTS


def _set_state(*, ready: bool | None = None, shutting_down: bool | None = None) -> None:
    with STATE_LOCK:
        if ready is not None:
            STATE["ready"] = ready
        if shutting_down is not None:
            STATE["shutting_down"] = shutting_down


def _get_state(key: str) -> bool:
    with STATE_LOCK:
        return bool(STATE[key])


@asynccontextmanager
async def lifespan(app: FastAPI):
    emit_event("startup")
    redis_ok = ping_redis()
    _set_state(ready=redis_ok, shutting_down=False)
    emit_event("ready", redis_connected=redis_ok)

    yield

    _set_state(ready=False, shutting_down=True)
    deadline = time.monotonic() + settings.graceful_shutdown_timeout_seconds
    while _get_active_requests() > 0 and time.monotonic() < deadline:
        await asyncio.sleep(0.5)
    emit_event("shutdown", active_requests=_get_active_requests())


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-User-Id"],
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = Field(default=None, max_length=128)


class AskResponse(BaseModel):
    question: str
    answer: str
    conversation_id: str
    history_messages: int
    model: str
    timestamp: str


def _conversation_id(user_id: str, requested_id: str | None) -> str:
    return requested_id.strip() if requested_id and requested_id.strip() else user_id


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    global REQUEST_COUNT, ERROR_COUNT
    REQUEST_COUNT += 1
    _increment_active_requests()
    start = time.perf_counter()

    try:
        if _get_state("shutting_down") and request.url.path not in {"/health", "/ready"}:
            return Response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=json.dumps({"detail": "Instance is shutting down"}),
                media_type="application/json",
            )

        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Request-Duration-Ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
        emit_event(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
        )
        return response
    except Exception:
        ERROR_COUNT += 1
        raise
    finally:
        _decrement_active_requests()


@app.get("/", tags=["Info"])
def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "endpoints": {
            "ask": "POST /ask (requires X-API-Key)",
            "history": "GET /conversations/{conversation_id}",
            "health": "GET /health",
            "ready": "GET /ready",
        },
    }


@app.post("/ask", response_model=AskResponse, tags=["Agent"])
async def ask_agent(
    body: AskRequest,
    request: Request,
    user_id: str = Depends(verify_api_key),
):
    check_rate_limit(user_id)

    conversation_id = _conversation_id(user_id, body.conversation_id)
    history = get_history(user_id, conversation_id)

    estimated_total_cost = estimate_cost(body.question)
    spent = check_budget(user_id, estimated_total_cost)
    append_message(user_id, conversation_id, "user", body.question)
    response_text, llm_source = llm_ask(body.question)
    append_message(user_id, conversation_id, "assistant", response_text)

    emit_event(
        "agent_call",
        user_id=user_id,
        conversation_id=conversation_id,
        history_messages=len(history),
        client=str(request.client.host) if request.client else "unknown",
        llm_source=llm_source,
        estimated_cost=estimated_total_cost,
        monthly_spend=spent,
    )

    return AskResponse(
        question=body.question,
        answer=response_text,
        conversation_id=conversation_id,
        history_messages=len(history) + 2,
        model=settings.llm_model,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/conversations/{conversation_id}", tags=["Agent"])
def get_conversation(conversation_id: str, user_id: str = Depends(verify_api_key)):
    history = get_history(user_id, conversation_id)
    if not history and not conversation_exists(user_id, conversation_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return {
        "conversation_id": conversation_id,
        "messages": history,
        "message_count": len(history),
    }


@app.get("/health", tags=["Operations"])
def health():
    redis_ok = ping_redis()
    return {
        "status": "ok" if redis_ok else "degraded",
        "version": settings.app_version,
        "environment": settings.environment,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "total_requests": REQUEST_COUNT,
        "redis_connected": redis_ok,
        "monthly_budget_usd": settings.monthly_budget_usd,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready", tags=["Operations"])
def ready():
    if _get_state("shutting_down") or not _get_state("ready"):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Not ready")
    if not ping_redis():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis not available")
    return {"ready": True, "in_flight_requests": _get_active_requests()}


@app.get("/metrics", tags=["Operations"])
def metrics(user_id: str = Depends(verify_api_key)):
    spend = get_monthly_spend(user_id)
    return {
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "total_requests": REQUEST_COUNT,
        "error_count": ERROR_COUNT,
        "monthly_cost_usd": round(spend, 4),
        "monthly_budget_usd": settings.monthly_budget_usd,
        "budget_used_pct": round((spend / settings.monthly_budget_usd * 100) if settings.monthly_budget_usd else 0, 1),
    }


def _handle_signal(signum, _frame):
    _set_state(ready=False, shutting_down=True)
    emit_event("signal", signum=signum)


signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


if __name__ == "__main__":
    emit_event("boot", host=settings.host, port=settings.port)
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        timeout_graceful_shutdown=settings.graceful_shutdown_timeout_seconds,
    )