# server/core/config.py
from __future__ import annotations
import os
import urllib.parse
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 👇 הוספה חשובה: טוענים את קובץ ה-.env לזיכרון
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

class Settings(BaseSettings):
    APP_NAME: str = "EventsAdvisor Server"
    ENV: str = "development"
    PORT: int = 8000

    DB_URL: str = Field(default="sqlite:///./eventhub.db", alias="DATABASE_URL")

    JWT_SECRET: str = "replace-me"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    GATEWAY_BASE_URL: str = "http://localhost:9000"
    TM_API_KEY: str | None = None

    OLLAMA_URL: str = "http://127.0.0.1:11434"
    AI_MODEL: str = "llama3.1"
    AI_TIMEOUT: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="EVENTHUB_",
        case_sensitive=False,
    )

    def resolve_db_url(self) -> str:
        raw = os.getenv("EVENTHUB_DATABASE_URL") or os.getenv("EVENTHUB_DB_URL") or self.DB_URL
        if "DRIVER=" in raw and "mssql+pyodbc" not in raw:
            return f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(raw)}"
        return raw

settings = Settings()
settings.DB_URL = settings.resolve_db_url()
