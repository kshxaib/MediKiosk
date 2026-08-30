"""Register all ORM models on Base.metadata."""
from app.models.alert import Alert, AlertSeverity, AlertStatus, AlertType
from app.models.answer import Answer
from app.models.case import Case, CaseEdit, CaseStatus, EditorType
from app.models.clinical_workflow import ClinicalWorkflow
from app.models.consent import Consent
from app.models.department import Department
from app.models.document import (
    Document,
    DocumentExtraction,
    DocumentType,
    ExtractionStatus,
)
from app.models.face_enrollment import FaceEnrollment
from app.models.hospital import Hospital
from app.models.intake_session import IntakeSession, SessionStatus
from app.models.medical_stream import MedicalStream
from app.models.patient import Patient
from app.models.patient_identifier import PatientIdentifier
from app.models.question import Question
from app.models.role import Role
from app.models.timeline_event import (
    InformationSource,
    TimelineEvent,
    TimelineEventType,
)
from app.models.user import User
from app.models.vital import Vital, VitalSource

__all__ = [
    "Alert",
    "AlertSeverity",
    "AlertStatus",
    "AlertType",
    "Answer",
    "Case",
    "CaseEdit",
    "CaseStatus",
    "ClinicalWorkflow",
    "Consent",
    "Department",
    "Document",
    "DocumentExtraction",
    "DocumentType",
    "EditorType",
    "ExtractionStatus",
    "FaceEnrollment",
    "Hospital",
    "InformationSource",
    "IntakeSession",
    "MedicalStream",
    "Patient",
    "PatientIdentifier",
    "Question",
    "Role",
    "SessionStatus",
    "TimelineEvent",
    "TimelineEventType",
    "User",
    "Vital",
    "VitalSource",
]
