from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    APP_NAME: str = "EventsAdvisor Server"
    ENV: str = "development"
    PORT: int = 8000

    DB_URL: str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=eventsdb_hadas.mssql.somee.com;DATABASE=eventsdb_hadas;UID=HDONAT_SQLLogin_1;PWD=udpqv6uev6;Encrypt=no;TrustServerCertificate=yes;"
    JWT_SECRET: str = "changeme"
    JWT_ALG: str = "HS256"

    GATEWAY_BASE_URL: str = "http://localhost:9000"
    OLLAMA_URL: str = "http://localhost:11434"
    
    TM_API_KEY: str | None = Field(default=None, alias="TM_API_KEY")


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
