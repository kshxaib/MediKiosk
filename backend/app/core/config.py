"""Centralized application configuration.

All runtime configuration is read from the environment (or an ``.env`` file)
through a single Pydantic ``Settings`` object. Future-phase secrets are
intentionally NOT declared here yet; ``extra="ignore"`` lets them sit in
``.env`` as documented placeholders without breaking Phase 1.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Application ---
    APP_NAME: str = "MediKiosk"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Database ---
    DATABASE_URL: str = (
        "postgresql+psycopg://medikiosk:medikiosk@localhost:5432/medikiosk"
    )

    # --- CORS ---
    # Comma-separated list of allowed origins, e.g.
    # "http://localhost:5173,http://localhost:3000".
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
