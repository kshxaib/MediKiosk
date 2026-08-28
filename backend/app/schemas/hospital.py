"""Hospital Pydantic schemas."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class HospitalRead(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
