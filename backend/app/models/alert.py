"""Alert ORM model — red flags and abnormal values (Phase 5C data layer).

Field baseline: PROJECT_REQUIREMENT.md §36A.20.

An alert is a prompt for clinical review, never a diagnosis (§26). The rule
engine that raises them is Phase 7; Phase 5C persists them and surfaces
whatever exists in the case summary.
"""
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.intake_session import IntakeSession
    from app.models.patient import Patient


class AlertType(str, enum.Enum):
    RED_FLAG = "RED_FLAG"
    ABNORMAL_VALUE = "ABNORMAL_VALUE"
    MEDICATION_REVIEW = "MEDICATION_REVIEW"


class AlertSeverity(str, enum.Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class Alert(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A flag raised for clinical review during an intake session."""

    __tablename__ = "alerts"

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
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    trigger_value: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default=AlertStatus.ACTIVE.value, nullable=False, index=True
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    acknowledged_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    session: Mapped["IntakeSession"] = relationship("IntakeSession", back_populates="alerts")
    patient: Mapped["Patient"] = relationship("Patient")

    def __repr__(self) -> str:
        return f"<Alert {self.alert_type}/{self.severity} session={self.session_id}>"
