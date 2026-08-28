"""Datetime helpers. All persisted timestamps are timezone-aware UTC."""
from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return the current time as a timezone-aware UTC ``datetime``."""
    return datetime.now(timezone.utc)
