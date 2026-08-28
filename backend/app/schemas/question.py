"""Question Pydantic schemas."""
import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class QuestionRead(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    question_code: str
    question_text: str
    question_type: str
    category: Optional[str] = None
    sequence: Optional[int] = None
    is_required: bool
    language: str
    validation_rules: Optional[dict[str, Any]] = None
    options: Optional[Any] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NextQuestionResponse(BaseModel):
    question_id: Optional[str] = None
    question: Optional[str] = None
    question_type: Optional[str] = None
    required: bool = False
    reason: Optional[str] = None
    category: Optional[str] = None
    options: Optional[Any] = None
    sequence: Optional[int] = None
    total_questions: int = 0
    completed_questions: int = 0
    is_last_question: bool = False
    completed: bool = False
    message: Optional[str] = None
