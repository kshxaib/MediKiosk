"""PatientIdentifier ORM model for polymorphic identifier abstraction."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class PatientIdentifier(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Identifier attached to a patient (e.g. MOBILE, future RFID)."""

    __tablename__ = "patient_identifiers"
    __table_args__ = (
        UniqueConstraint(
            "identifier_type",
            "identifier_value",
            name="uq_patient_identifiers_type_value",
        ),
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    identifier_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    identifier_value: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationship
    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="identifiers",
    )

    def __repr__(self) -> str:
        return f"<PatientIdentifier {self.identifier_type}:{self.identifier_value}>"
