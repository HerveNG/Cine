"""Application configuration.

All configuration is read from environment variables (see .env.example at the
repository root). Never hardcode secrets here.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    JWT_SECRET: str = "CHANGE_ME_IN_PRODUCTION"
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


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
