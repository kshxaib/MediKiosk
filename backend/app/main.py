"""FastAPI application entry point.

Builds the app via a factory so it can be constructed cleanly in tests as
well as by the ASGI server. Phase 1 wires only the system endpoints
(health, public config); business routers are added in later phases.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.schemas.system import HealthResponse
from app.services import system_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-initialize InsightFace ArcFace model at startup to avoid cold-start on first request."""
    try:
        from app.services.face import get_face_service
        get_face_service()
        logger.info("InsightFace ArcFace service warmed up successfully.")
    except Exception as exc:
        logger.warning("InsightFace warm-up skipped (non-fatal): %s", exc)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
        lifespan=lifespan,
    )

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    register_exception_handlers(app)

    # Mount API v1 router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Root health probe endpoint (handles direct /health calls from browsers/monitors)
    @app.get("/health", response_model=HealthResponse, include_in_schema=False)
    def root_health(response: Response, db: Session = Depends(get_db)) -> HealthResponse:
        result, healthy = system_service.get_health(db)
        if not healthy:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return result

    @app.get("/", include_in_schema=False)
    def root_index():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs_url": "/docs",
            "api_prefix": settings.API_V1_PREFIX,
        }

    return app


app = create_app()
