"""Tests for real InsightFace ArcFace biometric enrollment and live verification."""
import base64
import os
import random
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import create_app

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def get_base64_image(filename: str) -> str:
    path = os.path.join(FIXTURES_DIR, filename)
    with open(path, "rb") as f:
        data = f.read()
    return f"data:image/jpeg;base64,{base64.b64encode(data).decode('utf-8')}"


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


@pytest.fixture(scope="module")
def test_patient(client: TestClient) -> dict:
    mobile = f"9{random.randint(100000000, 999999999)}"
    res = client.post("/api/v1/patients", json={"full_name": "Biometric Test Subject", "mobile_number": mobile})
    assert res.status_code == 201
    return res.json()


def test_face_enroll_and_verify_pipeline(client: TestClient, test_patient: dict):
    patient_id = test_patient["id"]
    face_a_frame1_b64 = get_base64_image("person_a_frame1.jpg")
    face_a_frame2_b64 = get_base64_image("person_a_frame2.jpg")
    face_b_b64 = get_base64_image("person_b.jpg")
    blank_b64 = get_base64_image("blank.jpg")

    # 1. Blank frame with no face must return 422 Unprocessable Entity
    blank_res = client.post(
        "/api/v1/identity/face/enroll",
        json={"patient_id": patient_id, "image_base64": blank_b64},
    )
    assert blank_res.status_code == 422
    assert "No face detected" in blank_res.json()["detail"]

    # 2. Enroll Person A (frame 1)
    enroll_res = client.post(
        "/api/v1/identity/face/enroll",
        json={"patient_id": patient_id, "image_base64": face_a_frame1_b64},
    )
    assert enroll_res.status_code == 200
    assert enroll_res.json()["enrollment_status"] == "success"

    # 3. Verify with live capture of Person A (frame 2 - distinct webcam frame) -> must return verified=True
    verify_match_res = client.post(
        "/api/v1/identity/face/verify",
        json={"patient_id": patient_id, "image_base64": face_a_frame2_b64},
    )
    assert verify_match_res.status_code == 200
    assert verify_match_res.json()["verified"] is True
    assert "verified successfully" in verify_match_res.json()["message"]

    # 4. Verify with Person B (different human face) -> must return verified=False
    verify_diff_res = client.post(
        "/api/v1/identity/face/verify",
        json={"patient_id": patient_id, "image_base64": face_b_b64},
    )
    assert verify_diff_res.status_code == 200
    assert verify_diff_res.json()["verified"] is False
    assert "below threshold" in verify_diff_res.json()["message"]


def test_face_enroll_invalid_patient_returns_404(client: TestClient):
    random_id = str(uuid.uuid4())
    face_a_b64 = get_base64_image("person_a_frame1.jpg")

    res = client.post(
        "/api/v1/identity/face/enroll",
        json={"patient_id": random_id, "image_base64": face_a_b64},
    )
    assert res.status_code == 404
