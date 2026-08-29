"""Centralized application configuration.

All runtime configuration is read from the environment (or an ``.env`` file)
through a single Pydantic ``Settings`` object.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
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
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"

    # --- Authentication & JWT (Staff) ---
    JWT_SECRET_KEY: str = "dev_insecure_jwt_secret_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Biometric Face Recognition (Phase 3) ---
    FACE_MODEL_NAME: str = "buffalo_l"
    FACE_SIMILARITY_THRESHOLD: float = 0.50
    FACE_DETECTION_SIZE: int = 640

    # --- LLM / OpenAI (Phase 5B) ---
    OPENAI_API_KEY: str = ""
    # Deliberately a small, low-cost model: clinical intake needs structured
    # extraction and question selection, not frontier reasoning.
    OPENAI_MODEL: str = "gpt-5-mini"
    LLM_TIMEOUT_SECONDS: float = 15.0
    LLM_MAX_RETRIES: int = 2

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def llm_enabled(self) -> bool:
        """True only when a non-empty LLM API key is configured."""
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()