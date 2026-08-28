"""MedicalStream ORM model."""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.intake_session import IntakeSession


class MedicalStream(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Medical stream entity (MODERN_MEDICINE, AYUSH)."""

    __tablename__ = "medical_streams"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    intake_sessions: Mapped[list["IntakeSession"]] = relationship(
        "IntakeSession",
        back_populates="medical_stream",
    )

    def __repr__(self) -> str:
        return f"<MedicalStream {self.code} - {self.name}>"
