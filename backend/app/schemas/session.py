"""IntakeSession and Consent Pydantic schemas."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.department import DepartmentRead
from app.schemas.medical_stream import MedicalStreamRead
from app.schemas.patient import PatientRead


class ConsentCreate(BaseModel):
    patient_id: uuid.UUID
    consent_type: str = Field(default="CLINICAL_INTAKE", max_length=50)
    consent_text: str
    language: str = Field(default="en", max_length=10)
    is_granted: bool


class ConsentRead(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    patient_id: uuid.UUID
    consent_type: str
    consent_text: str
    language: str
    is_granted: bool
    consented_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionCreate(BaseModel):
    patient_id: uuid.UUID
    hospital_id: Optional[uuid.UUID] = None
    medical_stream_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    language: str = Field(default="en", max_length=10)


class SessionUpdate(BaseModel):
    medical_stream_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    language: Optional[str] = Field(default=None, max_length=10)
    status: Optional[str] = Field(default=None, max_length=50)


class SessionRead(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    hospital_id: uuid.UUID
    medical_stream_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    language: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    patient: Optional[PatientRead] = None
    medical_stream: Optional[MedicalStreamRead] = None
    department: Optional[DepartmentRead] = None
    consents: list[ConsentRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
