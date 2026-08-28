"""Language configuration endpoints."""
from fastapi import APIRouter
from app.schemas.language import LanguageRead
from app.services.config_service import ConfigService

router = APIRouter(prefix="/languages", tags=["Configuration"])


@router.get(
    "",
    response_model=list[LanguageRead],
    summary="List supported kiosk intake languages",
)
def list_languages() -> list[LanguageRead]:
    return ConfigService.get_languages()
