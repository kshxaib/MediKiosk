"""Identity Provider Base Abstraction."""
from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session

from app.models.patient import Patient


class IdentityProvider(ABC):
    """Abstract base class for patient identity lookup providers."""

    @abstractmethod
    def get_identifier_type(self) -> str:
        """Returns the identifier type string (e.g. MOBILE, RFID)."""
        pass

    @abstractmethod
    def lookup(self, db: Session, value: str) -> Optional[Patient]:
        """Looks up an active patient by their identifier value."""
        pass
