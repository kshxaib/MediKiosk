"""Patient business service."""
import uuid
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.patient_identifier import PatientIdentifier
from app.schemas.patient import PatientCreate, PatientUpdate
from app.services.identity.base import IdentityProvider
from app.services.identity.mobile_provider import MobileIdentityProvider
from app.utils.datetime import utcnow


class PatientService:
    """Handles patient registration, sequence code generation, and identifier management."""

    @staticmethod
    def generate_patient_code(db: Session) -> str:
        """Generate formatted sequential patient code: PAT-000001, PAT-000002..."""
        stmt = select(func.count(Patient.id))
        count = db.scalar(stmt) or 0
        return f"PAT-{count + 1:06d}"

    @classmethod
    def create_patient(
        cls,
        db: Session,
        data: PatientCreate,
    ) -> Patient:
        """Register a new patient and attach their primary mobile identifier."""
        # 1. Check if mobile already exists for an active patient
        mobile_provider = MobileIdentityProvider()
        existing = mobile_provider.lookup(db, data.mobile_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An active patient with mobile number {data.mobile_number} already exists ({existing.patient_code}).",
            )

        # 2. Generate unique patient code
        patient_code = cls.generate_patient_code(db)
        # Ensure code uniqueness if sequence collided
        while db.scalars(select(Patient).where(Patient.patient_code == patient_code)).first():
            stmt = select(func.count(Patient.id))
            count = (db.scalar(stmt) or 0) + 1
            patient_code = f"PAT-{count + 1:06d}"

        # 3. Create Patient entity
        patient = Patient(
            patient_code=patient_code,
            full_name=data.full_name.strip(),
            date_of_birth=data.date_of_birth,
            age=data.age,
            gender=data.gender,
            primary_language=data.primary_language or "en",
            email=data.email.strip().lower() if data.email else None,
            is_active=True,
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        db.add(patient)
        db.flush()

        # 4. Attach primary MOBILE identifier
        identifier = PatientIdentifier(
            patient_id=patient.id,
            identifier_type="MOBILE",
            identifier_value=mobile_provider.normalize_value(data.mobile_number),
            is_primary=True,
            is_active=True,
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        db.add(identifier)
        db.commit()
        db.refresh(patient)
        return patient

    @staticmethod
    def get_patient(db: Session, patient_id: uuid.UUID) -> Patient:
        """Retrieve an active patient by UUID."""
        patient = db.get(Patient, patient_id)
        if not patient or not patient.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found or inactive",
            )
        return patient

    @staticmethod
    def update_patient(
        db: Session,
        patient_id: uuid.UUID,
        data: PatientUpdate,
    ) -> Patient:
        """Update patient profile fields."""
        patient = db.get(Patient, patient_id)
        if not patient or not patient.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found or inactive",
            )

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(patient, key, value)

        patient.updated_at = utcnow()
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

    @staticmethod
    def lookup_by_provider(
        db: Session,
        provider: IdentityProvider,
        value: str,
    ) -> Optional[Patient]:
        """Generic lookup delegating to the supplied IdentityProvider."""
        return provider.lookup(db, value)
