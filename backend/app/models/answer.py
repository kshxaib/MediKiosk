"""Answer ORM model for storing clinically meaningful patient responses."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.intake_session import IntakeSession
    from app.models.patient import Patient
    from app.models.question import Question


class Answer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Clinically meaningful answer entity linked to an IntakeSession."""

    __tablename__ = "answers"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intake_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    raw_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    normalized_answer: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    answer_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="TOUCH", nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_patient_corrected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    session: Mapped["IntakeSession"] = relationship(
        "IntakeSession",
        back_populates="answers",
    )
    question: Mapped[Optional["Question"]] = relationship(
        "Question",
        back_populates="answers",
    )
    patient: Mapped["Patient"] = relationship(
        "Patient",
    )

    def __repr__(self) -> str:
        return f"<Answer session={self.session_id} q={self.question_id} type={self.answer_type}>"
