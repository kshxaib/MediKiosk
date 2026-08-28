"""ClinicalWorkflow ORM model."""
import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.medical_stream import MedicalStream
    from app.models.question import Question


class ClinicalWorkflow(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Configurable clinical history & case-taking workflow."""

    __tablename__ = "clinical_workflows"

    medical_stream_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("medical_streams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    configuration_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    medical_stream: Mapped["MedicalStream"] = relationship(
        "MedicalStream",
        lazy="joined",
    )
    department: Mapped[Optional["Department"]] = relationship(
        "Department",
        lazy="joined",
    )
    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="Question.sequence",
    )

    def __repr__(self) -> str:
        return f"<ClinicalWorkflow {self.code} - {self.name} (v{self.version})>"
