"""IntakeSession and Consent API endpoints."""
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.session import (
    ConsentCreate,
    ConsentRead,
    SessionCreate,
    SessionRead,
    SessionUpdate,
)
from app.services.session import SessionService

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post(
    "",
    response_model=SessionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new clinical intake session",
)
def create_session(
    payload: SessionCreate,
    db: Session = Depends(get_db),
) -> SessionRead:
    session = SessionService.create_session(db, payload)
    return SessionRead.model_validate(session)


@router.get(
    "/{session_id}",
    response_model=SessionRead,
    summary="Get intake session by ID",
)
def get_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> SessionRead:
    session = SessionService.get_session(db, session_id)
    return SessionRead.model_validate(session)


@router.patch(
    "/{session_id}",
    response_model=SessionRead,
    summary="Update intake session stream, department, language, or status",
)
def update_session(
    session_id: uuid.UUID,
    payload: SessionUpdate,
    db: Session = Depends(get_db),
) -> SessionRead:
    session = SessionService.update_session(db, session_id, payload)
    return SessionRead.model_validate(session)


@router.post(
    "/{session_id}/start",
    response_model=SessionRead,
    summary="Start the active intake clinical interview session",
)
def start_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> SessionRead:
    session = SessionService.start_session(db, session_id)
    return SessionRead.model_validate(session)


@router.post(
    "/{session_id}/complete",
    response_model=SessionRead,
    summary="Mark intake session as completed",
)
def complete_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> SessionRead:
    session = SessionService.complete_session(db, session_id)
    return SessionRead.model_validate(session)


@router.post(
    "/{session_id}/clear",
    response_model=SessionRead,
    summary="Cancel / reset intake session",
)
def clear_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> SessionRead:
    session = SessionService.clear_session(db, session_id)
    return SessionRead.model_validate(session)


@router.post(
    "/{session_id}/consent",
    response_model=ConsentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record explicit patient consent for an intake session",
)
def record_consent(
    session_id: uuid.UUID,
    payload: ConsentCreate,
    db: Session = Depends(get_db),
) -> ConsentRead:
    consent = SessionService.record_consent(db, session_id, payload)
    return ConsentRead.model_validate(consent)


@router.get(
    "/{session_id}/consent",
    response_model=list[ConsentRead],
    summary="Get consent records for an intake session",
)
def get_consents(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[ConsentRead]:
    consents = SessionService.get_consents(db, session_id)
    return [ConsentRead.model_validate(c) for c in consents]
