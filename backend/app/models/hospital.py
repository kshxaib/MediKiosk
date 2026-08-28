"""Hospital ORM model."""
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.intake_session import IntakeSession
    from app.models.user import User


class Hospital(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Hospital facility entity."""

    __tablename__ = "hospitals"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    departments: Mapped[list["Department"]] = relationship(
        "Department",
        back_populates="hospital",
        cascade="all, delete-orphan",
    )
    intake_sessions: Mapped[list["IntakeSession"]] = relationship(
        "IntakeSession",
        back_populates="hospital",
    )

    def __repr__(self) -> str:
        return f"<Hospital {self.code} - {self.name}>"
