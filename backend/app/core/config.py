from functools import lru_cache
import json
from pathlib import Path
from typing import Annotated

from pydantic import EmailStr, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str = "Mawahib Community Platform"
    ENVIRONMENT: str = "development"
    API_PREFIX: str = "/api"
    DATABASE_URL: str = "postgresql+psycopg://mawahib:mawahib@db:5432/mawahib"
    SECRET_KEY: str = Field(default="change-me-in-production", min_length=16)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    CORS_ORIGINS: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://localhost:8080",
        "https://mawahib-platform-1.onrender.com",
    ]
    ALLOWED_HOSTS: Annotated[list[str], NoDecode] = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "mawahib-platform.onrender.com",
        "mawahib-platform-1.onrender.com",
    ]
    DOCS_ENABLED: bool = True
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_MB: int = 15
    RATE_LIMIT_REQUESTS: int = 180
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    LOG_LEVEL: str = "INFO"
    AUTO_CREATE_TABLES: bool = False
    INITIAL_OWNER_EMAIL: EmailStr | None = None
    INITIAL_OWNER_PASSWORD: str | None = None
    INITIAL_OWNER_NAME: str = "Mawahib Owner"

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        return parse_env_list(value)

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value: str | list[str]) -> list[str]:
        return parse_env_list(value)

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.ENVIRONMENT.lower() in {"production", "prod"}:
            unsafe_secrets = {"change-me-in-production", "replace-with-a-long-random-secret-key"}
            if self.SECRET_KEY in unsafe_secrets:
                raise ValueError("SECRET_KEY must be changed before running in production.")
            if "*" in self.CORS_ORIGINS:
                raise ValueError("Wildcard CORS origins are not allowed in production.")
            if "*" in self.ALLOWED_HOSTS:
                raise ValueError("Wildcard allowed hosts are not allowed in production.")
            if self.DOCS_ENABLED:
                raise ValueError("DOCS_ENABLED must be false in production.")
        return self

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_MB * 1024 * 1024

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def should_create_tables_on_startup(self) -> bool:
        return self.AUTO_CREATE_TABLES or self.is_sqlite


def parse_env_list(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        parsed = json.loads(stripped)
        if not isinstance(parsed, list):
            raise ValueError("Expected a JSON list.")
        return [str(item).strip() for item in parsed if str(item).strip()]
    return [item.strip() for item in stripped.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
