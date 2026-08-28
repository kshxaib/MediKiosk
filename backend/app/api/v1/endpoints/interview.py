"""Clinical Interview AI Foundation API endpoints."""
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
    summary="Get next adaptive clinical interview question for the session",
)
def get_next_question(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> NextQuestionResponse:
    """
    Retrieves the next unanswered clinical intake question based on active workflow,
    session stream, department, language, and previously recorded answers.
    """
    return QuestionService.get_next_question(db, session_id)


@router.post(
    "/{session_id}/ai/answer",
    response_model=AnswerSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record clinically meaningful answer for a question in this session",
)
def record_answer(
    session_id: uuid.UUID,
    payload: AnswerCreate,
    db: Session = Depends(get_db),
) -> AnswerSubmissionResponse:
    """
    Validates session state, patient ownership, and persists structured/raw answer.
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
