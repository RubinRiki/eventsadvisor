# server/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # App
    APP_NAME: str = "EventsAdvisor Server"
    ENV: str = "development"
    PORT: int = 8000

    # DB
    DB_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Gateway (אם יש)
    GATEWAY_BASE_URL: str = "http://localhost:9000"
    TM_API_KEY: str | None = Field(default=None, alias="TM_API_KEY")

    # AI / Ollama
    OLLAMA_URL: str = "http://127.0.0.1:11434"
    AI_MODEL: str = "llama3.1"
    AI_TIMEOUT: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
