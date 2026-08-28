"""Question ORM model for adaptive clinical intake."""
import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.answer import Answer
    from app.models.clinical_workflow import ClinicalWorkflow


class Question(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Question entity defined within a clinical workflow."""

    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint(
            "workflow_id",
            "language",
            "question_code",
            name="uq_questions_workflow_lang_code",
        ),
    )

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinical_workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    sequence: Mapped[Optional[int]] = mapped_column(Integer, default=1, nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False, index=True)
    validation_rules: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    options: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)

    # Relationships
    workflow: Mapped["ClinicalWorkflow"] = relationship(
        "ClinicalWorkflow",
        back_populates="questions",
    )
    answers: Mapped[list["Answer"]] = relationship(
        "Answer",
        back_populates="question",
    )

    def __repr__(self) -> str:
        return f"<Question {self.question_code} [{self.question_type}] seq={self.sequence}>"
