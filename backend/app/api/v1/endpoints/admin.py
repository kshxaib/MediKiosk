"""Protected Admin demonstration routes."""
from typing import Any
from fastapi import APIRouter, Depends, status

from app.api.deps import require_role
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/dashboard-stats",
    status_code=status.HTTP_200_OK,
    summary="Admin-only diagnostics and system overview",
)
def get_admin_dashboard_stats(
    admin_user: User = Depends(require_role("ADMIN")),
) -> dict[str, Any]:
    """Admin-only diagnostic endpoint verifying ADMIN RBAC role access."""
    return {
        "status": "authorized",
        "message": "Admin access granted",
        "admin_email": admin_user.email,
        "role": admin_user.role.name,
    }
