"""Staff Authentication endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LogoutResponse,
    RefreshTokenRequest,
    TokenRefreshResponse,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Staff login (Email/Username + Password -> JWT)",
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate a staff user and issue JWT Access and Refresh tokens."""
    user = AuthService.authenticate_user(
        db=db,
        identifier=payload.identifier,
        password=payload.password,
    )
    return AuthService.issue_tokens(user)


@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
)
def refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> TokenRefreshResponse:
    """Exchange a valid refresh token for a new access token."""
    return AuthService.refresh_access_token(
        db=db,
        refresh_token=payload.refresh_token,
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Staff logout",
)
def logout(
    _current_user: User = Depends(get_current_active_user),
) -> LogoutResponse:
    """Acknowledge logout for the authenticated staff session."""
    return LogoutResponse(message="Successfully logged out")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current staff profile",
)
def get_current_staff_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Return the profile and role of the currently authenticated staff member."""
    return UserResponse.model_validate(current_user)
