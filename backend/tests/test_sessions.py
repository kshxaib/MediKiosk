"""Comprehensive unit and integration tests for Phase 4 Session and Consent."""
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


@pytest.fixture
def created_patient(client: TestClient) -> dict:
    """Helper to create a fresh registered patient for session tests."""
    payload = {
        "full_name": "Ananya Roy",
        "mobile_number": random_mobile(),
        "date_of_birth": "1994-08-20",
        "age": 32,
        "gender": "FEMALE",
        "primary_language": "en",
        "email": "ananya.roy@example.com",
    }
    res = client.post("/api/v1/patients", json=payload)
    assert res.status_code == 201, res.text
    return res.json()


# ==========================================
# 1. Configuration & Master Data Endpoints
# ==========================================

def test_get_languages(client: TestClient):
    res = client.get("/api/v1/languages")
    assert res.status_code == 200
    languages = res.json()
    assert len(languages) >= 2
    codes = [lang["code"] for lang in languages]
    assert "en" in codes
    assert "hi" in codes


def test_get_streams(client: TestClient):
    res = client.get("/api/v1/streams")
    assert res.status_code == 200
    streams = res.json()
    codes = [s["code"] for s in streams]
    assert "MODERN_MEDICINE" in codes
    assert "AYUSH" in codes


def test_get_stream_workflows_invalid(client: TestClient):
    fake_id = str(uuid.uuid4())
    res = client.get(f"/api/v1/streams/{fake_id}/workflows")
    assert res.status_code == 404


def test_get_departments(client: TestClient):
    res = client.get("/api/v1/departments")
    assert res.status_code == 200
    departments = res.json()
    assert len(departments) >= 6
    codes = [d["code"] for d in departments]
    assert "GEN_MED" in codes
    assert "CARDIO" in codes
    assert "NEURO" in codes
    assert "ORTHO" in codes
    assert "DERMA" in codes
    assert "AYURVEDA" in codes


def test_get_departments_filter_by_stream(client: TestClient):
    res_modern = client.get("/api/v1/departments?stream_code=MODERN_MEDICINE")
    assert res_modern.status_code == 200
    depts_modern = res_modern.json()
    assert any(d["code"] == "GEN_MED" for d in depts_modern)
    assert not any(d["code"] == "AYURVEDA" for d in depts_modern)

    res_ayush = client.get("/api/v1/departments?stream_code=AYUSH")
    assert res_ayush.status_code == 200
    depts_ayush = res_ayush.json()
    assert any(d["code"] == "AYURVEDA" for d in depts_ayush)
    assert not any(d["code"] == "GEN_MED" for d in depts_ayush)


# ==========================================
# 2. Session Creation & Validations
# ==========================================

def test_create_session_success(client: TestClient, created_patient: dict):
    payload = {
        "patient_id": created_patient["id"],
        "language": "hi",
    }
    res = client.post("/api/v1/sessions", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["patient_id"] == created_patient["id"]
    assert data["language"] == "hi"
    assert data["status"] == "IDENTITY_VERIFIED"
    assert "hospital_id" in data
    assert data["patient"]["full_name"] == created_patient["full_name"]


def test_create_session_invalid_patient_returns_404(client: TestClient):
    payload = {
        "patient_id": str(uuid.uuid4()),
        "language": "en",
    }
    res = client.post("/api/v1/sessions", json=payload)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_create_session_invalid_stream_returns_404(client: TestClient, created_patient: dict):
    payload = {
        "patient_id": created_patient["id"],
        "medical_stream_id": str(uuid.uuid4()),
    }
    res = client.post("/api/v1/sessions", json=payload)
    assert res.status_code == 404


def test_create_session_invalid_department_returns_404(client: TestClient, created_patient: dict):
    payload = {
        "patient_id": created_patient["id"],
        "department_id": str(uuid.uuid4()),
    }
    res = client.post("/api/v1/sessions", json=payload)
    assert res.status_code == 404


def test_get_session_by_id(client: TestClient, created_patient: dict):
    # 1. Create
    res_create = client.post("/api/v1/sessions", json={"patient_id": created_patient["id"]})
    session_id = res_create.json()["id"]

    # 2. Get
    res_get = client.get(f"/api/v1/sessions/{session_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == session_id
    assert res_get.json()["patient_id"] == created_patient["id"]


# ==========================================
# 3. Consent Flow & Ownership Checks
# ==========================================

def test_consent_granted_advances_status_to_consent_granted(client: TestClient, created_patient: dict):
    # 1. Create session
    res_sess = client.post("/api/v1/sessions", json={"patient_id": created_patient["id"]})
    session_id = res_sess.json()["id"]

    # 2. Grant consent
    consent_payload = {
        "patient_id": created_patient["id"],
        "consent_type": "CLINICAL_INTAKE",
        "consent_text": "I agree to have my symptoms collected and summarized.",
        "language": "en",
        "is_granted": True,
    }
    res_consent = client.post(f"/api/v1/sessions/{session_id}/consent", json=consent_payload)
    assert res_consent.status_code == 201, res_consent.text
    consent_data = res_consent.json()
    assert consent_data["is_granted"] is True
    assert consent_data["consented_at"] is not None
    assert consent_data["withdrawn_at"] is None

    # 3. Verify session status updated
    res_updated_sess = client.get(f"/api/v1/sessions/{session_id}")
    assert res_updated_sess.json()["status"] == "CONSENT_GRANTED"


def test_consent_declined_cancels_session(client: TestClient, created_patient: dict):
    res_sess = client.post("/api/v1/sessions", json={"patient_id": created_patient["id"]})
    session_id = res_sess.json()["id"]

    consent_payload = {
        "patient_id": created_patient["id"],
        "consent_type": "CLINICAL_INTAKE",
        "consent_text": "I do not agree.",
        "language": "en",
        "is_granted": False,
    }
    res_consent = client.post(f"/api/v1/sessions/{session_id}/consent", json=consent_payload)
    assert res_consent.status_code == 201
    assert res_consent.json()["is_granted"] is False
    assert res_consent.json()["withdrawn_at"] is not None

    # Verify session is cancelled
    res_updated_sess = client.get(f"/api/v1/sessions/{session_id}")
    assert res_updated_sess.json()["status"] == "CANCELLED"


def test_consent_ownership_mismatch_rejected(client: TestClient, created_patient: dict):
    res_sess = client.post("/api/v1/sessions", json={"patient_id": created_patient["id"]})
    session_id = res_sess.json()["id"]

    other_patient_id = str(uuid.uuid4())
    consent_payload = {
        "patient_id": other_patient_id,
        "consent_type": "CLINICAL_INTAKE",
        "consent_text": "I agree.",
        "language": "en",
        "is_granted": True,
    }
    res_consent = client.post(f"/api/v1/sessions/{session_id}/consent", json=consent_payload)
    assert res_consent.status_code == 403
    assert "does not match" in res_consent.json()["detail"].lower()


def test_get_session_consents(client: TestClient, created_patient: dict):
    res_sess = client.post("/api/v1/sessions", json={"patient_id": created_patient["id"]})
    session_id = res_sess.json()["id"]

    client.post(
        f"/api/v1/sessions/{session_id}/consent",
        json={
            "patient_id": created_patient["id"],
            "consent_type": "CLINICAL_INTAKE",
            "consent_text": "I agree to clinical intake.",
            "language": "en",
            "is_granted": True,
        },
    )

    res_list = client.get(f"/api/v1/sessions/{session_id}/consent")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1
    assert res_list.json()[0]["consent_text"] == "I agree to clinical intake."


# ==========================================
# 4. State Machine Transitions & Lifecycle
# ==========================================

def test_session_lifecycle_full_flow(client: TestClient, created_patient: dict):
    # 1. Create session
    res_create = client.post("/api/v1/sessions", json={"patient_id": created_patient["id"]})
    session_id = res_create.json()["id"]
    assert res_create.json()["status"] == "IDENTITY_VERIFIED"

    # 2. Grant consent -> status CONSENT_GRANTED
    client.post(
        f"/api/v1/sessions/{session_id}/consent",
        json={
            "patient_id": created_patient["id"],
            "consent_type": "CLINICAL_INTAKE",
            "consent_text": "I agree.",
            "language": "en",
            "is_granted": True,
        },
    )
    assert client.get(f"/api/v1/sessions/{session_id}").json()["status"] == "CONSENT_GRANTED"

    # 3. Select Stream and Department
    streams = client.get("/api/v1/streams").json()
    modern_stream = next(s for s in streams if s["code"] == "MODERN_MEDICINE")
    depts = client.get(f"/api/v1/departments?stream_code=MODERN_MEDICINE").json()
    cardio_dept = next(d for d in depts if d["code"] == "CARDIO")

    res_patch = client.patch(
        f"/api/v1/sessions/{session_id}",
        json={
            "medical_stream_id": modern_stream["id"],
            "department_id": cardio_dept["id"],
        },
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["medical_stream_id"] == modern_stream["id"]
    assert res_patch.json()["department_id"] == cardio_dept["id"]

    # 4. Start session -> status INTERVIEW_ACTIVE
    res_start = client.post(f"/api/v1/sessions/{session_id}/start")
    assert res_start.status_code == 200
    assert res_start.json()["status"] == "INTERVIEW_ACTIVE"
    assert res_start.json()["started_at"] is not None

    # 5. Progressive transitions to review, confirmation, summary, routing
    res_t1 = client.patch(f"/api/v1/sessions/{session_id}", json={"status": "REVIEW_PENDING"})
    assert res_t1.status_code == 200
    assert res_t1.json()["status"] == "REVIEW_PENDING"

    res_t2 = client.patch(f"/api/v1/sessions/{session_id}", json={"status": "PATIENT_CONFIRMED"})
    assert res_t2.status_code == 200
    assert res_t2.json()["status"] == "PATIENT_CONFIRMED"

    res_t3 = client.patch(f"/api/v1/sessions/{session_id}", json={"status": "SUMMARY_GENERATED"})
    assert res_t3.status_code == 200
    assert res_t3.json()["status"] == "SUMMARY_GENERATED"

    res_t4 = client.patch(f"/api/v1/sessions/{session_id}", json={"status": "CASE_ROUTED"})
    assert res_t4.status_code == 200
    assert res_t4.json()["status"] == "CASE_ROUTED"

    # 6. Complete session -> status COMPLETED
    res_complete = client.post(f"/api/v1/sessions/{session_id}/complete")
    assert res_complete.status_code == 200
    assert res_complete.json()["status"] == "COMPLETED"
    assert res_complete.json()["completed_at"] is not None


def test_invalid_state_transition_rejected(client: TestClient, created_patient: dict):
    res_create = client.post("/api/v1/sessions", json={"patient_id": created_patient["id"]})
    session_id = res_create.json()["id"]

    # Trying to jump directly from IDENTITY_VERIFIED to COMPLETED must fail with 400
    res_invalid = client.patch(f"/api/v1/sessions/{session_id}", json={"status": "COMPLETED"})
    assert res_invalid.status_code == 400
    assert "invalid session status transition" in res_invalid.json()["detail"].lower()


def test_start_session_without_stream_or_dept_fails(client: TestClient, created_patient: dict):
    res_create = client.post("/api/v1/sessions", json={"patient_id": created_patient["id"]})
    session_id = res_create.json()["id"]

    # Grant consent
    client.post(
        f"/api/v1/sessions/{session_id}/consent",
        json={
            "patient_id": created_patient["id"],
            "consent_type": "CLINICAL_INTAKE",
            "consent_text": "I agree.",
            "language": "en",
            "is_granted": True,
        },
    )

    # Attempt start without stream/dept
    res_start = client.post(f"/api/v1/sessions/{session_id}/start")
    assert res_start.status_code == 400
    assert "stream has not been selected" in res_start.json()["detail"].lower()


def test_clear_session_cancels_session(client: TestClient, created_patient: dict):
    res_create = client.post("/api/v1/sessions", json={"patient_id": created_patient["id"]})
    session_id = res_create.json()["id"]

    res_clear = client.post(f"/api/v1/sessions/{session_id}/clear")
    assert res_clear.status_code == 200
    assert res_clear.json()["status"] == "CANCELLED"

