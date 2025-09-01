from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "EventsAdvisor Server"
    ENV: str = "development"
    PORT: int = 8000

    DB_URL: str = "mongodb://localhost:27017/eventsdb"
    JWT_SECRET: str = "changeme"
    JWT_ALG: str = "HS256"

    GATEWAY_BASE_URL: str = "http://localhost:9000"
    OLLAMA_URL: str = "http://localhost:11434"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
