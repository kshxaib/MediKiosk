"""Patient API Endpoints."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.patient import (
    PatientCreate,
    PatientLookupResponse,
    PatientResponse,
    PatientUpdate,
)
from app.services.identity.mobile_provider import MobileIdentityProvider
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new patient",
)
def create_patient(
    data: PatientCreate,
    db: Session = Depends(get_db),
) -> PatientResponse:
    """Register a new patient and attach their primary mobile identifier."""
    patient = PatientService.create_patient(db, data)
    return PatientResponse.model_validate(patient)


@router.get(
    "/lookup",
    response_model=PatientLookupResponse,
    summary="Lookup patient by mobile number",
)
def lookup_patient_by_mobile(
    mobile: str = Query(..., min_length=10, description="10-digit mobile number"),
    db: Session = Depends(get_db),
) -> PatientLookupResponse:
    """
    Search for an existing active patient by mobile number.
    Returns 200 with found=false if patient does not exist.
    """
    provider = MobileIdentityProvider()
    patient = PatientService.lookup_by_provider(db, provider, mobile)

    if not patient:
        return PatientLookupResponse(
            found=False,
            patient=None,
            message="No patient found with this mobile number",
        )

    return PatientLookupResponse(
        found=True,
        patient=PatientResponse.model_validate(patient),
        message="Patient found",
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get patient profile by UUID",
)
def get_patient(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> PatientResponse:
    """Retrieve patient record by ID."""
    patient = PatientService.get_patient(db, patient_id)
    return PatientResponse.model_validate(patient)


@router.patch(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Update patient profile",
)
def update_patient(
    patient_id: uuid.UUID,
    data: PatientUpdate,
    db: Session = Depends(get_db),
) -> PatientResponse:
    """Update patient details."""
    patient = PatientService.update_patient(db, patient_id, data)
    return PatientResponse.model_validate(patient)
