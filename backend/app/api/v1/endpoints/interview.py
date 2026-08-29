"""Clinical Interview AI Foundation API endpoints (Phase 5B)."""
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.answer import AnswerCreate, AnswerRead, AnswerSubmissionResponse
from app.schemas.question import NextQuestionResponse
from app.services.interview import AnswerService, QuestionService

router = APIRouter(prefix="/sessions", tags=["Clinical Interview"])


@router.post(
    "/{session_id}/ai/next-question",
    response_model=NextQuestionResponse,
    summary="Get next adaptive clinical interview question (Phase 5B: LLM + fallback)",
)
def get_next_question(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> NextQuestionResponse:
    """
    Returns the next clinical question using adaptive LLM selection when
    available, with automatic deterministic fallback if the LLM is unavailable.

    Both paths skip questions whose information the session already has, so one
    patient answer covering several clinical categories does not produce
    duplicate follow-up questions. The backend — not the LLM — is the final
    authority on whether a category is satisfied.

    The patient-facing response is identical regardless of source (DB or LLM).
    Provider names, model names and LLM errors are never exposed to the patient.
    """
    return QuestionService.get_next_question_adaptive(db, session_id)


@router.post(
    "/{session_id}/ai/answer",
    response_model=AnswerSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record patient answer with bounded LLM extraction (Phase 5B)",
)
def record_answer(
    session_id: uuid.UUID,
    payload: AnswerCreate,
    db: Session = Depends(get_db),
) -> AnswerSubmissionResponse:
    """
    Persists the raw answer immediately, then attempts bounded LLM extraction.

    The raw answer is NEVER lost — if LLM extraction fails, the raw answer is
    preserved, no facts are fabricated, and confidence remains null.
    """
    return AnswerService.record_answer(db, session_id, payload)


@router.get(
    "/{session_id}/answers",
    response_model=list[AnswerRead],
    summary="List all recorded answers for an intake session",
)
def get_session_answers(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[AnswerRead]:
    answers = AnswerService.get_session_answers(db, session_id)
    return [AnswerRead.model_validate(a) for a in answers]
