"""MedicalStream and ClinicalWorkflow Pydantic schemas."""
import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class MedicalStreamRead(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClinicalWorkflowRead(BaseModel):
    id: uuid.UUID
    medical_stream_id: uuid.UUID
    department_id: Optional[uuid.UUID] = None
    name: str
    code: str
    description: Optional[str] = None
    version: str
    configuration_json: Optional[dict[str, Any]] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
