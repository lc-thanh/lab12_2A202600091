"""Production config — 12-Factor: tất cả từ environment variables."""
import logging
import os
from dataclasses import dataclass, field


@dataclass(slots=True)
class Settings:
    # Server
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")

    # App
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Production AI Agent"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"))

    # LLM
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))

    # Security
    agent_api_keys_raw: str = field(
        default_factory=lambda: os.getenv(
            "AGENT_API_KEYS",
            os.getenv("AGENT_API_KEY", "dev-key-change-me-in-production"),
        )
    )
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", "dev-jwt-secret-change-in-production"))
    allowed_origins_raw: str = field(default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "*"))

    # Rate limiting
    rate_limit_per_minute: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    )

    # Budget
    monthly_budget_usd: float = field(
        default_factory=lambda: float(os.getenv("MONTHLY_BUDGET_USD", os.getenv("DAILY_BUDGET_USD", "10.0")))
    )

    # Storage
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"))

    # Conversation / shutdown
    conversation_ttl_seconds: int = field(default_factory=lambda: int(os.getenv("CONVERSATION_TTL_SECONDS", "2592000")))
    max_history_messages: int = field(default_factory=lambda: int(os.getenv("MAX_HISTORY_MESSAGES", "20")))
    graceful_shutdown_timeout_seconds: int = field(default_factory=lambda: int(os.getenv("GRACEFUL_SHUTDOWN_TIMEOUT_SECONDS", "30")))

    # Backward compatibility with the lab skeleton and older docs
    daily_budget_usd: float = field(init=False)
    agent_api_keys: list[str] = field(init=False, repr=False)
    allowed_origins: list[str] = field(init=False, repr=False)
    agent_api_key: str = field(init=False)

    def __post_init__(self) -> None:
        self.agent_api_keys = [key.strip() for key in self.agent_api_keys_raw.split(",") if key.strip()]
        if not self.agent_api_keys:
            self.agent_api_keys = ["dev-key-change-me-in-production"]
        self.agent_api_key = self.agent_api_keys[0]
        self.allowed_origins = [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]
        if not self.allowed_origins:
            self.allowed_origins = ["*"]
        self.daily_budget_usd = self.monthly_budget_usd

    def validate(self):
        logger = logging.getLogger(__name__)
        if self.environment == "production":
            if any(key == "dev-key-change-me-in-production" for key in self.agent_api_keys):
                raise ValueError("AGENT_API_KEY must be set in production!")
            if self.jwt_secret == "dev-jwt-secret-change-in-production":
                raise ValueError("JWT_SECRET must be set in production!")
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not set - using mock LLM")
        return self


settings = Settings().validate()
