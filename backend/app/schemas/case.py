"""Case Pydantic schemas (Phase 5C)."""
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class CaseSummaryRequest(BaseModel):
    """Options for generating a case summary."""

    # Set False to force the deterministic narrative (used by tests and when a
    # site wants no LLM involvement at all). The structured summary is
    # deterministic either way.
    use_llm_narrative: bool = True


class CaseRead(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    patient_id: uuid.UUID
    hospital_id: uuid.UUID
    medical_stream_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    chief_complaint: Optional[str] = None
    # Structured clinical sections — the authoritative representation.
    summary: Optional[dict[str, Any]] = None
    # Human-readable rendering of `summary`. Never the source of truth.
    summary_text: Optional[str] = None
    status: str
    generated_by_model: Optional[str] = None
    generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseEditCreate(BaseModel):
    """A correction to one field of the structured summary.

    ``field_name`` is a dotted path into ``Case.summary``, e.g.
    ``current_consultation.chief_complaint``. Only paths that already exist may
    be corrected, so a correction cannot invent a new section.
    """

    field_name: str = Field(max_length=255)
    new_value: Any = None
    reason: Optional[str] = None
    # PATIENT corrections override the AI draft; DOCTOR corrections override
    # everything and are re-applied on every regeneration.
    editor_type: str = Field(default="PATIENT", max_length=50)
    edited_by: Optional[uuid.UUID] = None


class CaseEditRead(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    edited_by: Optional[uuid.UUID] = None
    editor_type: str
    field_name: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
