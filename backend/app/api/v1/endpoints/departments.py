"""Department configuration endpoints."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.department import ConsultantRead, DepartmentRead
from app.services.config_service import ConfigService

router = APIRouter(prefix="/departments", tags=["Configuration"])


@router.get(
    "",
    response_model=list[DepartmentRead],
    summary="List active clinical departments",
)
def list_departments(
    hospital_id: Optional[uuid.UUID] = Query(None, description="Filter by hospital UUID"),
    stream_code: Optional[str] = Query(None, description="Filter by stream code (MODERN_MEDICINE, AYUSH)"),
    db: Session = Depends(get_db),
) -> list[DepartmentRead]:
    departments = ConfigService.get_departments(db, hospital_id=hospital_id, stream_code=stream_code)
    return [DepartmentRead.model_validate(d) for d in departments]


@router.get(
    "/{department_id}/consultants",
    response_model=list[ConsultantRead],
    summary="List consultants / doctors assigned to a department",
)
def list_department_consultants(
    department_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[ConsultantRead]:
    department = ConfigService.get_department(db, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {department_id} not found",
        )
    return []
