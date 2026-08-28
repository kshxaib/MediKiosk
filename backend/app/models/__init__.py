"""Register all ORM models on Base.metadata."""
from app.models.role import Role
from app.models.user import User

__all__ = ["Role", "User"]
