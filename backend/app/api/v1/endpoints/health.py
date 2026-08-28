"""System health endpoint.

Actually verifies application health by checking database connectivity, and
returns a structured response. Reports HTTP 503 when a dependency is down so
external monitors can distinguish "up" from "degraded".
"""
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.system import HealthResponse
from app.services import system_service

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health(response: Response, db: Session = Depends(get_db)) -> HealthResponse:
    result, healthy = system_service.get_health(db)
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return result
