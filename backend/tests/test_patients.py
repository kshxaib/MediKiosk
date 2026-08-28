"""Tests for Patient CRUD, sequential code generation, and mobile identity lookup."""
import random
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def random_mobile() -> str:
    return f"9{random.randint(100000000, 999999999)}"


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_create_patient_success(client: TestClient):
    unique_mobile = random_mobile()
    payload = {
        "full_name": "Rohan Sharma",
        "mobile_number": unique_mobile,
        "date_of_birth": "1990-05-15",
        "age": 36,
        "gender": "MALE",
        "primary_language": "hi",
        "email": "rohan.sharma@example.com",
    }
    response = client.post("/api/v1/patients", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["full_name"] == "Rohan Sharma"
    assert data["patient_code"].startswith("PAT-")
    assert data["is_active"] is True
    assert "embedding_reference" not in data


def test_patient_code_sequential_generation(client: TestClient):
    r1 = client.post("/api/v1/patients", json={"full_name": "Patient One", "mobile_number": random_mobile()})
    r2 = client.post("/api/v1/patients", json={"full_name": "Patient Two", "mobile_number": random_mobile()})
    assert r1.status_code == 201
    assert r2.status_code == 201
    code1 = r1.json()["patient_code"]
    code2 = r2.json()["patient_code"]
    assert code1.startswith("PAT-")
    assert code2.startswith("PAT-")
    assert code1 != code2


def test_duplicate_mobile_rejected(client: TestClient):
    mobile = random_mobile()
    payload = {"full_name": "Duplicate Test", "mobile_number": mobile}
    r1 = client.post("/api/v1/patients", json=payload)
    assert r1.status_code == 201

    # Second creation with same active mobile must fail with 409 Conflict
    r2 = client.post("/api/v1/patients", json=payload)
    assert r2.status_code == 409
    assert "already exists" in r2.json()["detail"]


def test_lookup_existing_mobile(client: TestClient):
    mobile = random_mobile()
    client.post("/api/v1/patients", json={"full_name": "Lookup Test Patient", "mobile_number": mobile})

    response = client.get(f"/api/v1/patients/lookup?mobile={mobile}")
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True
    assert data["patient"] is not None
    assert data["patient"]["full_name"] == "Lookup Test Patient"


def test_lookup_unknown_mobile_returns_found_false(client: TestClient):
    response = client.get("/api/v1/patients/lookup?mobile=9999900000")
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is False
    assert data["patient"] is None
    assert "No patient found" in data["message"]


def test_get_patient_by_id(client: TestClient):
    created = client.post("/api/v1/patients", json={"full_name": "Fetch Test", "mobile_number": random_mobile()}).json()
    patient_id = created["id"]

    response = client.get(f"/api/v1/patients/{patient_id}")
    assert response.status_code == 200
    assert response.json()["id"] == patient_id
    assert response.json()["full_name"] == "Fetch Test"


def test_update_patient(client: TestClient):
    created = client.post("/api/v1/patients", json={"full_name": "Initial Name", "mobile_number": random_mobile()}).json()
    patient_id = created["id"]

    response = client.patch(f"/api/v1/patients/{patient_id}", json={"full_name": "Updated Name", "age": 42})
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"
    assert response.json()["age"] == 42
