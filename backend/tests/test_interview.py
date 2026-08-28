"""Comprehensive test suite for Phase 5A AI Clinical Interview Foundation."""
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
def initialized_session(client: TestClient) -> dict:
    """Helper to register a patient, create a session, grant consent, and set stream/dept."""
    # 1. Create Patient
    patient_payload = {
        "full_name": "Vikram Malhotra",
        "mobile_number": random_mobile(),
        "age": 42,
        "gender": "MALE",
        "primary_language": "en",
    }
    res_pat = client.post("/api/v1/patients", json=patient_payload)
    assert res_pat.status_code == 201
    patient = res_pat.json()

    # 2. Get Modern Medicine Stream & General Medicine Department
    streams = client.get("/api/v1/streams").json()
    mod_stream = next(s for s in streams if s["code"] == "MODERN_MEDICINE")

    depts = client.get(f"/api/v1/departments?stream_code=MODERN_MEDICINE").json()
    gen_med = next(d for d in depts if d["code"] == "GEN_MED")

    # 3. Create Session
    session_payload = {
        "patient_id": patient["id"],
        "medical_stream_id": mod_stream["id"],
        "department_id": gen_med["id"],
        "language": "en",
    }
    res_sess = client.post("/api/v1/sessions", json=session_payload)
    assert res_sess.status_code == 201
    session = res_sess.json()

    # 4. Grant Consent -> sets status to CONSENT_GRANTED
    client.post(
        f"/api/v1/sessions/{session['id']}/consent",
        json={
            "patient_id": patient["id"],
            "consent_type": "CLINICAL_INTAKE",
            "consent_text": "I give consent.",
            "language": "en",
            "is_granted": True,
        },
    )

    return {
        "patient": patient,
        "session_id": session["id"],
        "stream": mod_stream,
        "department": gen_med,
    }


def test_get_stream_workflows(client: TestClient, initialized_session: dict):
    stream_id = initialized_session["stream"]["id"]
    res = client.get(f"/api/v1/streams/{stream_id}/workflows")
    assert res.status_code == 200
    workflows = res.json()
    assert len(workflows) >= 1
    assert any(w["code"] == "MOD_GEN_MED_V1" for w in workflows)


def test_first_question_retrieval(client: TestClient, initialized_session: dict):
    session_id = initialized_session["session_id"]
    res = client.post(f"/api/v1/sessions/{session_id}/ai/next-question")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["completed"] is False
    assert data["question_id"] is not None
    assert "primary health concern" in data["question"].lower()
    assert data["question_type"] == "TEXT"
    assert data["required"] is True
    assert data["sequence"] == 1
    assert data["total_questions"] >= 5
    assert data["completed_questions"] == 0


def test_answer_submission_and_skipping_answered(client: TestClient, initialized_session: dict):
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    # 1. Fetch Q1
    res_q1 = client.post(f"/api/v1/sessions/{session_id}/ai/next-question")
    q1_id = res_q1.json()["question_id"]

    # 2. Answer Q1
    ans1_payload = {
        "patient_id": patient_id,
        "question_id": q1_id,
        "raw_answer": "Severe headache and dull pain behind the eyes for two days",
        "normalized_answer": {"symptom": "headache", "location": "retro-orbital"},
        "answer_type": "TEXT",
        "source": "TOUCH",
    }
    res_ans1 = client.post(f"/api/v1/sessions/{session_id}/ai/answer", json=ans1_payload)
    assert res_ans1.status_code == 201
    assert res_ans1.json()["saved"] is True
    assert res_ans1.json()["next_question_available"] is True

    # 3. Next question should now be Q2 (Onset)
    res_q2 = client.post(f"/api/v1/sessions/{session_id}/ai/next-question")
    assert res_q2.status_code == 200
    assert res_q2.json()["sequence"] == 2
    assert res_q2.json()["completed_questions"] == 1
    assert "when" in res_q2.json()["question"].lower()


def test_full_question_lifecycle_to_completion(client: TestClient, initialized_session: dict):
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    # Answer all remaining questions in the workflow
    while True:
        res_q = client.post(f"/api/v1/sessions/{session_id}/ai/next-question")
        assert res_q.status_code == 200
        q_data = res_q.json()
        if q_data["completed"]:
            break

        q_type = q_data["question_type"]
        if q_type == "NUMBER":
            raw_val = "7"
            norm = {"severity_score": 7}
        elif q_type == "YES_NO":
            raw_val = "YES"
            norm = {"fever_present": True}
        elif q_type == "SINGLE_CHOICE":
            raw_val = "Getting Worse"
            norm = {"trend": "worsening"}
        else:
            raw_val = "Started yesterday morning"
            norm = {"onset": "1 day"}

        res_ans = client.post(
            f"/api/v1/sessions/{session_id}/ai/answer",
            json={
                "patient_id": patient_id,
                "question_id": q_data["question_id"],
                "raw_answer": raw_val,
                "normalized_answer": norm,
                "answer_type": q_type,
                "source": "TOUCH",
            },
        )
        assert res_ans.status_code == 201

    # After loop, calling next-question returns completed: True
    res_final = client.post(f"/api/v1/sessions/{session_id}/ai/next-question")
    assert res_final.status_code == 200
    assert res_final.json()["completed"] is True
    assert res_final.json()["completed_questions"] >= 5

    # Verify answers listing endpoint
    res_list = client.get(f"/api/v1/sessions/{session_id}/answers")
    assert res_list.status_code == 200
    answers = res_list.json()
    assert len(answers) >= 5


def test_answer_patient_ownership_mismatch_rejected(client: TestClient, initialized_session: dict):
    session_id = initialized_session["session_id"]
    res_q = client.post(f"/api/v1/sessions/{session_id}/ai/next-question")
    q_id = res_q.json()["question_id"]

    other_patient_id = str(uuid.uuid4())
    res_ans = client.post(
        f"/api/v1/sessions/{session_id}/ai/answer",
        json={
            "patient_id": other_patient_id,
            "question_id": q_id,
            "raw_answer": "Should fail",
            "answer_type": "TEXT",
        },
    )
    assert res_ans.status_code == 403


def test_answer_invalid_question_id_rejected(client: TestClient, initialized_session: dict):
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    res_ans = client.post(
        f"/api/v1/sessions/{session_id}/ai/answer",
        json={
            "patient_id": patient_id,
            "question_id": str(uuid.uuid4()),
            "raw_answer": "Invalid question ID",
            "answer_type": "TEXT",
        },
    )
    assert res_ans.status_code == 404


def test_ayush_workflow_questions_retrieval(client: TestClient):
    # Register patient & create AYUSH session
    pat_res = client.post(
        "/api/v1/patients",
        json={
            "full_name": "Pooja Hegde",
            "mobile_number": random_mobile(),
            "primary_language": "en",
        },
    )
    patient = pat_res.json()

    streams = client.get("/api/v1/streams").json()
    ayush_stream = next(s for s in streams if s["code"] == "AYUSH")
    depts = client.get("/api/v1/departments?stream_code=AYUSH").json()
    ayurveda_dept = next(d for d in depts if d["code"] == "AYURVEDA")

    sess_res = client.post(
        "/api/v1/sessions",
        json={
            "patient_id": patient["id"],
            "medical_stream_id": ayush_stream["id"],
            "department_id": ayurveda_dept["id"],
            "language": "en",
        },
    )
    session = sess_res.json()

    # Grant consent
    client.post(
        f"/api/v1/sessions/{session['id']}/consent",
        json={
            "patient_id": patient["id"],
            "consent_type": "CLINICAL_INTAKE",
            "consent_text": "I agree",
            "language": "en",
            "is_granted": True,
        },
    )

    # Next question should return Ayurvedic intake question
    res_q = client.post(f"/api/v1/sessions/{session['id']}/ai/next-question")
    assert res_q.status_code == 200
    data = res_q.json()
    assert data["question_id"] is not None
    assert "imbalance" in data["question"].lower()
    assert data["total_questions"] >= 4
