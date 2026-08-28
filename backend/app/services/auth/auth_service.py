"""Staff authentication service."""
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.user import User
from app.schemas.auth import TokenRefreshResponse, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.utils.datetime import utcnow


class AuthService:
    """Handles staff authentication, token issuance, and token refresh."""

    @staticmethod
    def authenticate_user(
        db: Session,
        identifier: str,
        password: str,
    ) -> User:
        """Authenticate a user by email/username and password."""
        stmt = select(User).where(User.email == identifier.strip().lower())
        user = db.scalars(stmt).first()

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )

        user.last_login_at = utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def issue_tokens(user: User) -> TokenResponse:
        """Generate access and refresh tokens for an authenticated user."""
        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.name,
        )
        refresh_token = create_refresh_token(user_id=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    def refresh_access_token(
        db: Session,
        refresh_token: str,
    ) -> TokenRefreshResponse:
        """Validate a refresh token and issue a new access token."""
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type for refresh",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token subject",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Malformed user ID in token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        new_access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.name,
        )
        return TokenRefreshResponse(
            access_token=new_access_token,
            token_type="bearer",
        )
