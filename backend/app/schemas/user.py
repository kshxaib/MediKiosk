"""User and Role Pydantic response schemas."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RoleResponse(BaseModel):
    """Staff role schema."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None


class UserResponse(BaseModel):
    """Sanitized staff user profile (never exposes password_hash)."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hospital_id: Optional[uuid.UUID] = None
    full_name: str
    email: str = Field(..., description="Email address")
    phone: Optional[str] = None
    is_active: bool
    role: RoleResponse
    created_at: datetime
    last_login_at: Optional[datetime] = None
