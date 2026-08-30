"""TimelineEvent ORM model — longitudinal patient history (Phase 5C data layer).

Field baseline: PROJECT_REQUIREMENT.md §36A.19. Every event points back to the
record it came from via ``source_type`` + ``source_id`` (§23 source tracking).
"""
import enum
import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class TimelineEventType(str, enum.Enum):
    DIAGNOSIS = "DIAGNOSIS"
    PRESCRIPTION = "PRESCRIPTION"
    LAB_REPORT = "LAB_REPORT"
    HOSPITAL_ADMISSION = "HOSPITAL_ADMISSION"
    PROCEDURE = "PROCEDURE"
    CURRENT_COMPLAINT = "CURRENT_COMPLAINT"
    VITAL = "VITAL"
    ALLERGY = "ALLERGY"
    FAMILY_HISTORY = "FAMILY_HISTORY"
    PERSONAL_HISTORY = "PERSONAL_HISTORY"


class InformationSource(str, enum.Enum):
    """Canonical provenance values (§23).

    Used by timeline events and by every item in the generated case summary so a
    doctor can always tell where a statement came from.
    """

    PATIENT_INTERVIEW = "PATIENT_INTERVIEW"
    DOCUMENT_OCR = "DOCUMENT_OCR"
    VITAL_MEASUREMENT = "VITAL_MEASUREMENT"
    PATIENT_CORRECTION = "PATIENT_CORRECTION"
    DOCTOR_VERIFICATION = "DOCTOR_VERIFICATION"


class TimelineEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """One dated entry in a patient's longitudinal history."""

    __tablename__ = "timeline_events"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intake_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)

    patient: Mapped["Patient"] = relationship("Patient")

    def __repr__(self) -> str:
        return f"<TimelineEvent {self.event_type} {self.event_date} patient={self.patient_id}>"
