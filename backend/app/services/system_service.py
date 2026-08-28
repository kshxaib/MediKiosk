"""System service: health checks and public configuration assembly.

Endpoint handlers stay thin; the actual logic (DB ping, config shaping) lives
here so it is unit-testable and reusable.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.system import HealthChecks, HealthResponse, PublicConfig
from app.utils.datetime import utcnow


def check_database(db: Session) -> bool:
    """Return ``True`` if a trivial query against Postgres succeeds."""
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_health(db: Session) -> tuple[HealthResponse, bool]:
    """Build the health response and report overall healthy/unhealthy."""
    database_ok = check_database(db)
    response = HealthResponse(
        status="healthy" if database_ok else "unhealthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=utcnow(),
        checks=HealthChecks(database="ok" if database_ok else "unavailable"),
    )
    return response, database_ok


def get_public_config() -> PublicConfig:
    return PublicConfig(
        app_name=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
        api_version=settings.APP_VERSION,
    )
