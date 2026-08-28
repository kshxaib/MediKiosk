"""Department and Consultant Pydantic schemas."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DepartmentRead(BaseModel):
    id: uuid.UUID
    hospital_id: uuid.UUID
    name: str
    code: str
    description: Optional[str] = None
    stream_code: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConsultantRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    hospital_id: uuid.UUID
    department_id: uuid.UUID
    medical_stream_id: Optional[uuid.UUID] = None
    full_name: str
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
