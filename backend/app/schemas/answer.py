"""Answer Pydantic schemas."""
import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class AnswerCreate(BaseModel):
    patient_id: Optional[uuid.UUID] = None
    question_id: Optional[uuid.UUID] = None
    raw_answer: Optional[str] = None
    normalized_answer: Optional[dict[str, Any]] = None
    answer_type: str = Field(default="TEXT", max_length=50)
    source: str = Field(default="TOUCH", max_length=50)
    confidence: Optional[float] = None
    is_patient_corrected: bool = False


class AnswerRead(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    question_id: Optional[uuid.UUID] = None
    patient_id: uuid.UUID
    raw_answer: Optional[str] = None
    normalized_answer: Optional[dict[str, Any]] = None
    answer_type: str
    source: str
    confidence: Optional[float] = None
    answered_at: datetime
    is_patient_corrected: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnswerSubmissionResponse(BaseModel):
    answer_id: uuid.UUID
    saved: bool = True
    next_question_available: bool = False
    message: str = "Answer saved successfully"
