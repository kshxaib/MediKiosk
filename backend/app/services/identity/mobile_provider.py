"""Mobile Number Identity Provider."""
import re
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.patient_identifier import PatientIdentifier
from app.services.identity.base import IdentityProvider


class MobileIdentityProvider(IdentityProvider):
    """Identifies patients using their 10-digit mobile number."""

    def get_identifier_type(self) -> str:
        return "MOBILE"

    def normalize_value(self, value: str) -> str:
        cleaned = re.sub(r"\D", "", value)
        return cleaned[-10:] if len(cleaned) >= 10 else cleaned

    def lookup(self, db: Session, value: str) -> Optional[Patient]:
        normalized = self.normalize_value(value)
        if not normalized:
            return None

        stmt = (
            select(Patient)
            .join(PatientIdentifier, Patient.id == PatientIdentifier.patient_id)
            .where(
                PatientIdentifier.identifier_type == "MOBILE",
                PatientIdentifier.identifier_value == normalized,
                PatientIdentifier.is_active == True,
                Patient.is_active == True,
            )
        )
        return db.scalars(stmt).first()
