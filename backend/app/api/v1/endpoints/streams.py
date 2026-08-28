"""Medical Stream configuration endpoints."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.medical_stream import ClinicalWorkflowRead, MedicalStreamRead
from app.services.config_service import ConfigService

router = APIRouter(prefix="/streams", tags=["Configuration"])


@router.get(
    "",
    response_model=list[MedicalStreamRead],
    summary="List active medical streams (Modern Medicine, AYUSH)",
)
def list_streams(db: Session = Depends(get_db)) -> list[MedicalStreamRead]:
    streams = ConfigService.get_streams(db)
    return [MedicalStreamRead.model_validate(s) for s in streams]


@router.get(
    "/{stream_id}/workflows",
    response_model=list[ClinicalWorkflowRead],
    summary="Get clinical workflows for a medical stream",
)
def get_stream_workflows(
    stream_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[ClinicalWorkflowRead]:
    stream = ConfigService.get_stream(db, stream_id)
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medical stream with ID {stream_id} not found",
        )
    # Returns configured workflows (empty list if none configured yet in Phase 4)
    return []
