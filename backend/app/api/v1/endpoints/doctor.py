"""Protected Doctor demonstration routes."""
from typing import Any
from fastapi import APIRouter, Depends, status

from app.api.deps import require_role
from app.models.user import User

router = APIRouter(prefix="/doctor", tags=["doctor"])


@router.get(
    "/profile",
    status_code=status.HTTP_200_OK,
    summary="Doctor portal profile access",
)
def get_doctor_profile(
    doctor_user: User = Depends(require_role("DOCTOR", "ADMIN")),
) -> dict[str, Any]:
    """Doctor route verifying DOCTOR (or supervisory ADMIN) role access."""
    return {
        "status": "authorized",
        "message": "Doctor portal access granted",
        "doctor_id": str(doctor_user.id),
        "doctor_name": doctor_user.full_name,
        "doctor_email": doctor_user.email,
        "role": doctor_user.role.name,
    }
