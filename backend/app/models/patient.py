"""Patient ORM model."""
import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.face_enrollment import FaceEnrollment
    from app.models.patient_identifier import PatientIdentifier


class Patient(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Patient core entity."""

    __tablename__ = "patients"

    patient_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    date_of_birth: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    age: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    gender: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    primary_language: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        default="en",
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    identifiers: Mapped[list["PatientIdentifier"]] = relationship(
        "PatientIdentifier",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    face_enrollments: Mapped[list["FaceEnrollment"]] = relationship(
        "FaceEnrollment",
        back_populates="patient",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Patient {self.patient_code} - {self.full_name}>"
