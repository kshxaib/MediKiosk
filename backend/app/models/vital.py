"""Vital ORM model — manually entered measurements (Phase 5C data layer).

Field baseline: PROJECT_REQUIREMENT.md §36A.15. The current MVP source is
MANUAL; future hardware (BP_DEVICE, SPO2_DEVICE, THERMOMETER, SCALE) becomes
another value of ``source`` without schema change.
"""
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.intake_session import IntakeSession
    from app.models.patient import Patient


class VitalSource(str, enum.Enum):
    MANUAL = "MANUAL"
    BP_DEVICE = "BP_DEVICE"
    SPO2_DEVICE = "SPO2_DEVICE"
    THERMOMETER = "THERMOMETER"
    SCALE = "SCALE"


class Vital(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Vital signs recorded for one intake session."""

    __tablename__ = "vitals"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intake_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    weight_kg: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    height_cm: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    systolic_bp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    diastolic_bp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pulse_bpm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    temperature_c: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    spo2_percent: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    source: Mapped[str] = mapped_column(
        String(50), default=VitalSource.MANUAL.value, nullable=False
    )
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    session: Mapped["IntakeSession"] = relationship("IntakeSession", back_populates="vitals")
    patient: Mapped["Patient"] = relationship("Patient")

    def __repr__(self) -> str:
        return f"<Vital session={self.session_id} source={self.source}>"
