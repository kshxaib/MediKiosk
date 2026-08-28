"""Consent ORM model."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.intake_session import IntakeSession
    from app.models.patient import Patient


class Consent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Explicit patient consent record linked to an IntakeSession."""

    __tablename__ = "consents"

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
    consent_type: Mapped[str] = mapped_column(
        String(50),
        default="CLINICAL_INTAKE",
        nullable=False,
    )
    consent_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False,
    )
    is_granted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )
    consented_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    session: Mapped["IntakeSession"] = relationship(
        "IntakeSession",
        back_populates="consents",
    )
    patient: Mapped["Patient"] = relationship(
        "Patient",
    )

    def __repr__(self) -> str:
        return f"<Consent session={self.session_id} granted={self.is_granted}>"
