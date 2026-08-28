"""Register all ORM models on Base.metadata."""
from app.models.consent import Consent
from app.models.department import Department
from app.models.face_enrollment import FaceEnrollment
from app.models.hospital import Hospital
from app.models.intake_session import IntakeSession, SessionStatus
from app.models.medical_stream import MedicalStream
from app.models.patient import Patient
from app.models.patient_identifier import PatientIdentifier
from app.models.role import Role
from app.models.user import User

__all__ = [
    "Consent",
    "Department",
    "FaceEnrollment",
    "Hospital",
    "IntakeSession",
    "MedicalStream",
    "Patient",
    "PatientIdentifier",
    "Role",
    "SessionStatus",
    "User",
]
