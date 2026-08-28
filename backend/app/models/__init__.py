"""Register all ORM models on Base.metadata."""
from app.models.face_enrollment import FaceEnrollment
from app.models.patient import Patient
from app.models.patient_identifier import PatientIdentifier
from app.models.role import Role
from app.models.user import User

__all__ = [
    "FaceEnrollment",
    "Patient",
    "PatientIdentifier",
    "Role",
    "User",
]
