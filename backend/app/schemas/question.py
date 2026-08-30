"""Question Pydantic schemas."""
import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


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
    # Phase 5B (kiosk): read-only passthrough of the question's validation rules
    # (e.g. {"min": 1, "max": 10}) so the touchscreen can render a correctly
    # bounded numeric control instead of hard-coding a 1-10 scale. SEVERITY is
    # 1-10 but the AYUSH sleep-hours question is 0-24. No clinical logic here —
    # the backend still validates nothing differently.
    validation_rules: Optional[dict[str, Any]] = None
    total_questions: int = 0
    completed_questions: int = 0
    is_last_question: bool = False
    completed: bool = False
    message: Optional[str] = None
    # Phase 5B: indicates if LLM was used (backend telemetry, not shown in UI)
    llm_used: bool = False
    # Phase 5B: clinical categories already satisfied for this session, either by
    # an answered question or by facts extracted from an earlier answer.
    # Backend telemetry — not rendered in the kiosk UI.
    satisfied_categories: list[str] = Field(default_factory=list)
    # Phase 5B: True when this question asks the patient to refine information
    # that is already partially known (e.g. qualitative "severe" -> numeric 1-10)
    # rather than being asked for the first time.
    is_refinement: bool = False
