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
    cookie_samesite: str = "lax"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
