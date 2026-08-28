"""Authentication and JWT request/response schemas."""
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Staff login payload."""
    email: Optional[str] = Field(default=None, description="Email address")
    username: Optional[str] = Field(default=None, description="Username/email alias")
    password: str = Field(..., min_length=1, description="Plaintext password")

    @property
    def identifier(self) -> str:
        """Returns email or username depending on which was provided."""
        val = self.email or self.username
        if not val:
            raise ValueError("Email or username is required")
        return val.strip()


class TokenResponse(BaseModel):
    """Response returned upon successful login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Payload to request a new access token using a refresh token."""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Response containing a renewed access token."""
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    """Logout confirmation response."""
    message: str = "Successfully logged out"


class TokenPayload(BaseModel):
    """Decoded JWT payload structure."""
    sub: str
    email: Optional[str] = None
    role: Optional[str] = None
    type: str
    exp: int
    iat: int
