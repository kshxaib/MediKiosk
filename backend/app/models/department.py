"""Department ORM model."""
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.hospital import Hospital
    from app.models.intake_session import IntakeSession


class Department(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Hospital Department entity (GEN_MED, CARDIO, NEURO, etc.)."""

    __tablename__ = "departments"

    hospital_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hospitals.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stream_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    hospital: Mapped["Hospital"] = relationship(
        "Hospital",
        back_populates="departments",
    )
    intake_sessions: Mapped[list["IntakeSession"]] = relationship(
        "IntakeSession",
        back_populates="department",
    )

    def __repr__(self) -> str:
        return f"<Department {self.code} - {self.name}>"
