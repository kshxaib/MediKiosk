"""Public (non-secret) configuration endpoint consumed by the frontend."""
from fastapi import APIRouter

from app.schemas.system import PublicConfig
from app.services import system_service

router = APIRouter(tags=["system"])


@router.get("/config/public", response_model=PublicConfig)
def public_config() -> PublicConfig:
    return system_service.get_public_config()
