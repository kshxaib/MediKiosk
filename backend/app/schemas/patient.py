"""Patient schemas."""
import re
import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PatientCreate(BaseModel):
    """Payload to register a new patient."""
    full_name: str = Field(..., min_length=2, max_length=255, description="Full patient name")
    mobile_number: str = Field(..., min_length=10, max_length=15, description="10-digit mobile number")
    date_of_birth: Optional[date] = Field(default=None, description="Date of birth")
    age: Optional[int] = Field(default=None, ge=0, le=130, description="Age in years")
    gender: Optional[str] = Field(default=None, max_length=20, description="Gender (MALE, FEMALE, OTHER)")
    primary_language: Optional[str] = Field(default="en", max_length=10, description="Language code")
    email: Optional[str] = Field(default=None, max_length=255, description="Optional email")

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if len(cleaned) < 10:
            raise ValueError("Mobile number must contain at least 10 digits")
        # Standardize to last 10 digits for Indian standard mobile format
        return cleaned[-10:] if len(cleaned) >= 10 else cleaned


class PatientUpdate(BaseModel):
    """Payload to update patient profile."""
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    date_of_birth: Optional[date] = None
    age: Optional[int] = Field(default=None, ge=0, le=130)
    gender: Optional[str] = Field(default=None, max_length=20)
    primary_language: Optional[str] = Field(default=None, max_length=10)
    email: Optional[str] = Field(default=None, max_length=255)


class PatientResponse(BaseModel):
    """Safe public patient response (never leaks internal biometric vectors)."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_code: str
    full_name: str
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    primary_language: Optional[str] = "en"
    email: Optional[str] = None
    is_active: bool
    created_at: datetime


class PatientLookupResponse(BaseModel):
    """Structured lookup response."""
    found: bool
    patient: Optional[PatientResponse] = None
    message: str

PatientRead = PatientResponse

