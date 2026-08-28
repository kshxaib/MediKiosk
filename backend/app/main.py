"""FastAPI application entry point.

Builds the app via a factory so it can be constructed cleanly in tests as
well as by the ASGI server. Phase 1 wires only the system endpoints
(health, public config); business routers are added in later phases.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
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
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.on_event("startup")
    async def warm_up_face_service() -> None:
        """Pre-initialize InsightFace ArcFace model at startup to avoid cold-start on first request."""
        try:
            from app.services.face import get_face_service
            get_face_service()
            logger.info("InsightFace ArcFace service warmed up successfully.")
        except Exception as exc:
            logger.warning("InsightFace warm-up skipped (non-fatal): %s", exc)

    return app


app = create_app()

