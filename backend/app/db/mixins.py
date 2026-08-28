"""Reusable model mixins (infrastructure only — no tables defined here).

These provide the UUID primary key and UTC timestamp columns mandated by the
requirements. They are consumed by concrete models starting in Phase 2; Phase 1
ships them so the schema conventions are fixed up front.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.utils.datetime import utcnow


class UUIDPrimaryKeyMixin:
    """Adds a UUID ``id`` primary key (never a mobile number / RFID / biometric)."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    """Adds UTC ``created_at`` / ``updated_at`` columns."""

    created_at: Mapped[datetime] = mapped_column(
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
