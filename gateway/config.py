import os
from pydantic import BaseSettings, AnyHttpUrl

class Settings(BaseSettings):
    APP_NAME: str = "EventHub BFF"
    SERVER_BASE_URL: AnyHttpUrl = os.getenv("SERVER_BASE_URL", "http://127.0.0.1:8000")
    COOKIE_NAME: str = os.getenv("COOKIE_NAME", "gw_token")
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "lax")

settings = Settings()
