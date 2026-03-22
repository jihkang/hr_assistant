from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "HR Assistant Backend"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["http://localhost:3000"]
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/hr_assistant"
    secret_key: str = "change-this-secret-key-at-least-32-bytes"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    access_cookie_name: str = "hr_access_token"
    refresh_cookie_name: str = "hr_refresh_token"
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        normalized_value = value.strip()
        if len(normalized_value) < 32:
            raise ValueError("secret_key must be at least 32 characters long.")
        return normalized_value

    @field_validator("cookie_samesite", mode="before")
    @classmethod
    def normalize_cookie_samesite(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @model_validator(mode="after")
    def validate_cookie_policy(self) -> "Settings":
        if self.cookie_samesite == "none" and not self.cookie_secure:
            raise ValueError("cookie_secure must be true when cookie_samesite is 'none'.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


class SettingsProxy:
    def __getattr__(self, name: str):
        return getattr(get_settings(), name)


settings = SettingsProxy()
