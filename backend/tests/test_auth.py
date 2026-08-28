"""Comprehensive test suite for Phase 2 Staff Authentication and RBAC."""
import uuid
from datetime import timedelta
import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password, verify_password
from app.db.session import SessionLocal
from app.main import create_app
from app.models.role import Role
from app.models.user import User
from app.services.auth.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.utils.datetime import utcnow


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


@pytest.fixture(scope="module")
def setup_test_users():
    """Ensure baseline test roles and users exist in the test DB."""
    with SessionLocal() as db:
        # 1. Ensure Roles
        admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
        if not admin_role:
            admin_role = Role(
                id=uuid.uuid4(),
                name="ADMIN",
                description="Administrator",
            )
            db.add(admin_role)
            db.flush()

        doc_role = db.query(Role).filter(Role.name == "DOCTOR").first()
        if not doc_role:
            doc_role = Role(
                id=uuid.uuid4(),
                name="DOCTOR",
                description="Doctor",
            )
            db.add(doc_role)
            db.flush()

        # 2. Ensure Active Admin
        admin_user = db.query(User).filter(User.email == "test_admin@medikiosk.local").first()
        if not admin_user:
            admin_user = User(
                id=uuid.uuid4(),
                email="test_admin@medikiosk.local",
                full_name="Test Admin User",
                password_hash=hash_password("AdminPass123!"),
                role_id=admin_role.id,
                is_active=True,
            )
            db.add(admin_user)

        # 3. Ensure Active Doctor
        doc_user = db.query(User).filter(User.email == "test_doctor@medikiosk.local").first()
        if not doc_user:
            doc_user = User(
                id=uuid.uuid4(),
                email="test_doctor@medikiosk.local",
                full_name="Test Doctor User",
                password_hash=hash_password("DoctorPass123!"),
                role_id=doc_role.id,
                is_active=True,
            )
            db.add(doc_user)

        # 4. Ensure Inactive User
        inactive_user = db.query(User).filter(User.email == "test_inactive@medikiosk.local").first()
        if not inactive_user:
            inactive_user = User(
                id=uuid.uuid4(),
                email="test_inactive@medikiosk.local",
                full_name="Inactive Staff",
                password_hash=hash_password("InactivePass123!"),
                role_id=doc_role.id,
                is_active=False,
            )
            db.add(inactive_user)

        db.commit()


# --- Unit Security Tests ---

def test_password_hashing_and_verification():
    raw_pass = "MySuperSecretPass!2026"
    hashed = hash_password(raw_pass)

    assert hashed != raw_pass
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_creation_and_claims_validation():
    user_id = uuid.uuid4()
    email = "staff@medikiosk.local"
    role = "DOCTOR"

    # Access token
    access_token = create_access_token(user_id=user_id, email=email, role=role)
    payload = decode_token(access_token)

    assert payload["sub"] == str(user_id)
    assert payload["email"] == email
    assert payload["role"] == role
    assert payload["type"] == "access"
    assert payload["exp"] > payload["iat"]

    # Refresh token
    refresh_token = create_refresh_token(user_id=user_id)
    r_payload = decode_token(refresh_token)

    assert r_payload["sub"] == str(user_id)
    assert r_payload["type"] == "refresh"
    assert r_payload["exp"] > r_payload["iat"]


def test_jwt_expired_token_rejected():
    user_id = uuid.uuid4()
    expired_token = create_access_token(
        user_id=user_id,
        email="expired@medikiosk.local",
        role="ADMIN",
        expires_delta=timedelta(seconds=-10),
    )

    with pytest.raises(Exception) as exc_info:
        decode_token(expired_token)
    assert "expired" in str(exc_info.value).lower()


# --- Endpoint Integration Tests ---

def test_login_success(client: TestClient, setup_test_users):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test_admin@medikiosk.local", "password": "AdminPass123!"},
    )
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test_admin@medikiosk.local"
    assert data["user"]["role"]["name"] == "ADMIN"
    # Security: Ensure password_hash is never exposed
    assert "password_hash" not in data["user"]
    assert "password_hash" not in str(data)


def test_login_wrong_password_rejected(client: TestClient, setup_test_users):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test_admin@medikiosk.local", "password": "IncorrectPassword"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_unknown_email_rejected(client: TestClient, setup_test_users):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@medikiosk.local", "password": "AnyPassword123!"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_inactive_user_rejected(client: TestClient, setup_test_users):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test_inactive@medikiosk.local", "password": "InactivePass123!"},
    )
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()


def test_auth_me_authenticated(client: TestClient, setup_test_users):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test_doctor@medikiosk.local", "password": "DoctorPass123!"},
    )
    token = login_resp.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_doctor@medikiosk.local"
    assert data["role"]["name"] == "DOCTOR"
    assert "password_hash" not in data


def test_auth_me_unauthenticated_rejected(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_refresh_token_success(client: TestClient, setup_test_users):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test_doctor@medikiosk.local", "password": "DoctorPass123!"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token_with_access_token_rejected(client: TestClient, setup_test_users):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test_doctor@medikiosk.local", "password": "DoctorPass123!"},
    )
    access_token = login_resp.json()["access_token"]

    # Trying to refresh using an access token must be rejected
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )
    assert response.status_code == 401


def test_logout_endpoint(client: TestClient, setup_test_users):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test_doctor@medikiosk.local", "password": "DoctorPass123!"},
    )
    token = login_resp.json()["access_token"]

    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"


# --- RBAC Authorization Tests ---

def test_admin_route_as_admin_allowed(client: TestClient, setup_test_users):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test_admin@medikiosk.local", "password": "AdminPass123!"},
    )
    token = login_resp.json()["access_token"]

    response = client.get(
        "/api/v1/admin/dashboard-stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "ADMIN"


def test_admin_route_as_doctor_forbidden(client: TestClient, setup_test_users):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test_doctor@medikiosk.local", "password": "DoctorPass123!"},
    )
    token = login_resp.json()["access_token"]

    response = client.get(
        "/api/v1/admin/dashboard-stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert "Operation not permitted" in response.json()["detail"]


def test_doctor_route_as_doctor_allowed(client: TestClient, setup_test_users):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test_doctor@medikiosk.local", "password": "DoctorPass123!"},
    )
    token = login_resp.json()["access_token"]

    response = client.get(
        "/api/v1/doctor/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "DOCTOR"


def test_doctor_route_as_admin_allowed_for_supervision(client: TestClient, setup_test_users):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test_admin@medikiosk.local", "password": "AdminPass123!"},
    )
    token = login_resp.json()["access_token"]

    response = client.get(
        "/api/v1/doctor/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
