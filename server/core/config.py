# -*- coding: utf-8 -*-
# ================================================================
#  EventHub Server — core/config.py
#  Created by: Riki Rubin & Hadas Donat
# ================================================================
"""
📌 Purpose (Explanation Box)
Centralized Pydantic Settings for the FastAPI backend.

Highlights:
- Loads from environment variables and optional `.env`.
- Provides safe local defaults for dev.
- Supports aliases (e.g., DB_URL or DATABASE_URL).
- Normalizes CORS origins from comma-separated string to list.

How to override (example .env):
    EVENTHUB_APP_NAME=EventHub API
    EVENTHUB_ENV=development
    EVENTHUB_PORT=8000

    EVENTHUB_DB_URL=sqlite:///./eventhub.db
    # or: EVENTHUB_DATABASE_URL=sqlite:///./eventhub.db

    EVENTHUB_JWT_SECRET=please-change-me
    EVENTHUB_JWT_ALG=HS256
    EVENTHUB_ACCESS_TOKEN_EXPIRE_MINUTES=60

    EVENTHUB_GATEWAY_BASE_URL=http://localhost:9000
    EVENTHUB_TM_API_KEY=

    EVENTHUB_OLLAMA_URL=http://127.0.0.1:11434
    EVENTHUB_AI_MODEL=llama3.1
    EVENTHUB_AI_TIMEOUT=15

    EVENTHUB_ALLOW_ORIGINS=*
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    # ---------------- App ----------------
    APP_NAME: str = Field(default="EventHub API")
    ENV: str = Field(default="development")
    PORT: int = Field(default=8000)

    # ---------------- Database ----------------
    # Accept both DB_URL and DATABASE_URL via aliasing
    DB_URL: str = Field(default="sqlite:///./eventhub.db", alias="DATABASE_URL")

    # ---------------- JWT ----------------
    JWT_SECRET: str = Field(default="please-change-me")
    JWT_ALG: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)

    # ---------------- Gateway / External ----------------
    GATEWAY_BASE_URL: str = Field(default="http://localhost:9000")
    TM_API_KEY: Optional[str] = Field(default=None, alias="TM_API_KEY")

    # ---------------- AI / Ollama ----------------
    OLLAMA_URL: str = Field(default="http://127.0.0.1:11434")
    AI_MODEL: str = Field(default="llama3.1")
    AI_TIMEOUT: int = Field(default=15)

    # ---------------- CORS ----------------
    # Comma-separated in .env (e.g., "http://localhost:3000,http://127.0.0.1:8000")
    ALLOW_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    @field_validator("ALLOW_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, v):
        if v is None:
            return ["*"]
        if isinstance(v, list):
            return v
        return [p.strip() for p in str(v).split(",") if p and p.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        # Prefix all env vars to avoid collisions (e.g., EVENTHUB_DB_URL)
        env_prefix="EVENTHUB_",
        case_sensitive=False,
    )


settings = Settings()
