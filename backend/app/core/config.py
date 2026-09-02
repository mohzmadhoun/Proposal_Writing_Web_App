from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Proposal Writing Web App API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    frontend_origin: str = "http://localhost:5173"
    jwt_secret_key: str = "change-this-secret-key-in-production-32chars"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/proposal_app"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
