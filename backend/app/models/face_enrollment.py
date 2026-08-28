"""FaceEnrollment ORM model."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import UUIDPrimaryKeyMixin
from app.utils.datetime import utcnow

if TYPE_CHECKING:
    from app.models.patient import Patient


class FaceEnrollment(Base, UUIDPrimaryKeyMixin):
    """Stores biometric face enrollment embedding references."""

    __tablename__ = "face_enrollments"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    embedding_reference: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="insightface_buffalo_l_arcface",
    )
    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="1.0.1",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE",
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    # Relationship
    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="face_enrollments",
    )

    def __repr__(self) -> str:
        return f"<FaceEnrollment patient={self.patient_id} status={self.status}>"
