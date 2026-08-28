"""IntakeSession ORM model and Status enumeration."""
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.answer import Answer
    from app.models.consent import Consent
    from app.models.department import Department
    from app.models.hospital import Hospital
    from app.models.medical_stream import MedicalStream
    from app.models.patient import Patient


class SessionStatus(str, enum.Enum):
    CREATED = "CREATED"
    IDENTITY_VERIFIED = "IDENTITY_VERIFIED"
    CONSENT_GRANTED = "CONSENT_GRANTED"
    INTERVIEW_ACTIVE = "INTERVIEW_ACTIVE"
    REVIEW_PENDING = "REVIEW_PENDING"
    PATIENT_CONFIRMED = "PATIENT_CONFIRMED"
    SUMMARY_GENERATED = "SUMMARY_GENERATED"
    CASE_ROUTED = "CASE_ROUTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class IntakeSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Patient clinical intake session entity."""

    __tablename__ = "intake_sessions"

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
    language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=SessionStatus.CREATED.value,
        nullable=False,
        index=True,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    patient: Mapped["Patient"] = relationship(
        "Patient",
        lazy="joined",
    )
    hospital: Mapped["Hospital"] = relationship(
        "Hospital",
        back_populates="intake_sessions",
        lazy="joined",
    )
    medical_stream: Mapped[Optional["MedicalStream"]] = relationship(
        "MedicalStream",
        back_populates="intake_sessions",
        lazy="joined",
    )
    department: Mapped[Optional["Department"]] = relationship(
        "Department",
        back_populates="intake_sessions",
        lazy="joined",
    )
    answers: Mapped[list["Answer"]] = relationship(
        "Answer",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    consents: Mapped[list["Consent"]] = relationship(
        "Consent",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<IntakeSession {self.id} [{self.status}] patient={self.patient_id}>"
