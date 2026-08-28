"""Role ORM model for RBAC."""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import UUIDPrimaryKeyMixin
from app.utils.datetime import utcnow

if TYPE_CHECKING:
    from app.models.user import User


class Role(Base, UUIDPrimaryKeyMixin):
    """Staff roles (e.g. ADMIN, DOCTOR)."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Role {self.name}>"
