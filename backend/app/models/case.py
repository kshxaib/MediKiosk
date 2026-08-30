"""Case and CaseEdit ORM models (Phase 5C).

Field baseline: PROJECT_REQUIREMENT.md §36A.21 and §36A.23.

``Case`` is the Phase 5C deliverable: the structured case summary generated from
one intake session. ``Case.summary`` is structured JSONB (§36C.7) — the
authoritative artifact, assembled deterministically by the backend.
``summary_text`` is only a human-readable rendering of it.

``CaseEdit`` records patient and doctor corrections. Patient corrections
override the AI draft for the final patient-confirmed representation (§28), and
doctor-verified fields must never be silently overwritten by AI (§33).
"""
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.hospital import Hospital
    from app.models.intake_session import IntakeSession
    from app.models.medical_stream import MedicalStream
    from app.models.patient import Patient


class CaseStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PATIENT_CONFIRMED = "PATIENT_CONFIRMED"
    DOCTOR_VERIFIED = "DOCTOR_VERIFIED"
    COMPLETED = "COMPLETED"


class EditorType(str, enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    SYSTEM = "SYSTEM"


class Case(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """The consultation package generated from one intake session."""

    __tablename__ = "cases"
    __table_args__ = (
        # §36B: cases.session_id UNIQUE — one case per intake session.
        UniqueConstraint("session_id", name="uq_cases_session_id"),
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intake_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    hospital_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hospitals.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    medical_stream_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("medical_streams.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    chief_complaint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Structured clinical sections — the authoritative representation.
    summary: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    # Optional human-readable rendering of `summary`. Never the source of truth.
    summary_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default=CaseStatus.DRAFT.value, nullable=False, index=True
    )
    generated_by_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    session: Mapped["IntakeSession"] = relationship("IntakeSession", back_populates="case")
    patient: Mapped["Patient"] = relationship("Patient", lazy="joined")
    hospital: Mapped["Hospital"] = relationship("Hospital")
    medical_stream: Mapped[Optional["MedicalStream"]] = relationship("MedicalStream")
    department: Mapped[Optional["Department"]] = relationship("Department")
    edits: Mapped[list["CaseEdit"]] = relationship(
        "CaseEdit",
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseEdit.created_at",
    )

    def __repr__(self) -> str:
        return f"<Case {self.id} [{self.status}] session={self.session_id}>"


class CaseEdit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """One correction applied to a case field by a patient, doctor, or the system.

    ``field_name`` is a dotted path into ``Case.summary``, e.g.
    ``current_consultation.chief_complaint``.
    """

    __tablename__ = "case_edits"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    edited_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    editor_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    old_value: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    case: Mapped["Case"] = relationship("Case", back_populates="edits")

    def __repr__(self) -> str:
        return f"<CaseEdit {self.editor_type} {self.field_name} case={self.case_id}>"
