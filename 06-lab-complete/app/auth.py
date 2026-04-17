"""API key authentication."""
import hashlib
import hmac

from fastapi import Header, HTTPException, status

from app.config import settings


def _derive_user_id(api_key: str, explicit_user_id: str | None) -> str:
    if explicit_user_id and explicit_user_id.strip():
        return explicit_user_id.strip()
    digest = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    return f"user-{digest[:16]}"


def verify_api_key(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    x_user_id: str | None = Header(None, alias="X-User-Id"),
) -> str:
    # Explicitly check for missing API key
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )
    
    # Check if API key is valid
    if not any(hmac.compare_digest(x_api_key, expected) for expected in settings.agent_api_keys):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    return _derive_user_id(x_api_key, x_user_id)