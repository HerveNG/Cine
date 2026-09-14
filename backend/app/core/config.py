"""Application configuration.

All configuration is read from environment variables (see .env.example at the
repository root). Never hardcode secrets here.
"""
from functools import lru_cache
from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_JWT_SECRET = "CHANGE_ME_IN_PRODUCTION"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    PROJECT_NAME: str = "FilmFund Africa"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # --- Database ---
    # Example: postgresql+psycopg2://user:password@localhost:5432/filmfund
    DATABASE_URL: str = "postgresql+psycopg2://filmfund:filmfund@localhost:5432/filmfund"

    # --- Auth / JWT ---
    JWT_SECRET: str = _DEFAULT_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h, fine for an MVP

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # --- AI provider (abstraction layer, see app/services/ai) ---
    AI_PROVIDER: str = "none"  # "openai" | "anthropic" | "local" | "none"
    AI_API_KEY: str = ""
    AI_MODEL: str = ""

    # --- Automation (n8n) ---
    N8N_WEBHOOK_URL: str = ""
    # Shared secret n8n must send (header X-N8N-Secret) when calling
    # POST /api/v1/integrations/n8n/funding-update. Empty = endpoint
    # disabled (503) — never accept unauthenticated writes from outside.
    N8N_WEBHOOK_SECRET: str = ""

    # --- Email (SMTP) ---
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # --- Storage ---
    STORAGE_URL: str = ""

    @model_validator(mode="after")
    def _forbid_default_jwt_secret_in_production(self) -> "Settings":
        # Signing tokens with the placeholder that's committed in this
        # public repo would let anyone forge a valid session for any
        # user. Fail fast rather than run insecurely.
        if self.ENVIRONMENT == "production" and self.JWT_SECRET == _DEFAULT_JWT_SECRET:
            raise ValueError(
                "JWT_SECRET must be set to a real random value when ENVIRONMENT=production."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
