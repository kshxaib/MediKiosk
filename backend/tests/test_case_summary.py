"""Phase 5C Structured AI Case Summary tests.

The structured summary is assembled deterministically, so these tests run with
the LLM disabled by default (see conftest) and assert on the structured JSONB
rather than on prose. The LLM narrative path is exercised separately with a stub.

Phase 6/7 ingestion pipelines do not exist yet, so historical fixtures
(documents, extractions, timeline events) and vitals/alerts are seeded directly
into PostgreSQL — which is exactly the data those pipelines will later write.
"""
import random
import uuid
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.session import SessionLocal
from app.main import create_app
from app.models.alert import Alert, AlertSeverity, AlertStatus, AlertType
from app.models.case import Case, CaseStatus, EditorType
from app.models.document import (
    Document,
    DocumentExtraction,
    DocumentType,
    ExtractionStatus,
)
from app.models.intake_session import IntakeSession, SessionStatus
from app.models.timeline_event import InformationSource, TimelineEvent, TimelineEventType
from app.models.vital import Vital, VitalSource
from app.services.llm.schemas import (
    AnswerExtraction,
    ExtractedFact,
    SymptomDetail,
)
from app.utils.datetime import utcnow

HINDI_ANSWER = "I have severe stomach pain for 3 days, with vomiting since yesterday"

MODERN_SECTIONS = (
    "past_medical_history",
    "past_surgical_history",
    "drug_history",
    "allergy_history",
    "family_history",
    "personal_history",
    "previous_investigations",
)


def random_mobile() -> str:
    return f"9{random.randint(100000000, 999999999)}"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


# ─── LLM stubbing ─────────────────────────────────────────────────────────────

STOMACH_EXTRACTION = AnswerExtraction(
    primary_complaint=SymptomDetail(
        symptom="stomach pain", duration="3 days", severity="severe"
    ),
    associated_symptoms=[SymptomDetail(symptom="vomiting", onset="1 day")],
    categories_satisfied=["CHIEF_COMPLAINT", "ONSET", "SEVERITY"],
    confidence=0.95,
)


def use_extraction(extraction):
    """Enable the Phase 5B extractor with a stubbed result."""
    from contextlib import ExitStack

    svc = MagicMock()
    svc.extract_answer.return_value = extraction
    stack = ExitStack()
    stack.enter_context(patch.object(settings, "OPENAI_API_KEY", "test-key"))
    stack.enter_context(patch("app.services.llm.get_llm_service", return_value=svc))
    return stack


# ─── Session helpers ──────────────────────────────────────────────────────────

def _new_patient(client: TestClient, name="Summary Test") -> dict:
    res = client.post(
        "/api/v1/patients",
        json={
            "full_name": name,
            "mobile_number": random_mobile(),
            "age": 47,
            "gender": "MALE",
            "primary_language": "en",
        },
    )
    assert res.status_code == 201, res.text
    return res.json()


def _new_session(client: TestClient, patient: dict, stream="MODERN_MEDICINE", dept="GEN_MED") -> str:
    st = next(s for s in client.get("/api/v1/streams").json() if s["code"] == stream)
    dp = next(
        d for d in client.get(f"/api/v1/departments?stream_code={stream}").json()
        if d["code"] == dept
    )
    sess = client.post(
        "/api/v1/sessions",
        json={
            "patient_id": patient["id"],
            "medical_stream_id": st["id"],
            "department_id": dp["id"],
            "language": "en",
        },
    ).json()
    client.post(
        f"/api/v1/sessions/{sess['id']}/consent",
        json={
            "patient_id": patient["id"],
            "consent_type": "CLINICAL_INTAKE",
            "consent_text": "I consent.",
            "language": "en",
            "is_granted": True,
        },
    )
    return sess["id"]


def _answer_interview(client: TestClient, session_id: str, patient_id: str, first_raw: str):
    """Answer the whole workflow, using the stubbed extractor on the first answer."""
    with use_extraction(STOMACH_EXTRACTION):
        q = client.post(f"/api/v1/sessions/{session_id}/ai/next-question").json()
        client.post(
            f"/api/v1/sessions/{session_id}/ai/answer",
            json={
                "patient_id": patient_id,
                "question_id": q["question_id"],
                "raw_answer": first_raw,
                "normalized_answer": {"text": first_raw},
                "answer_type": "TEXT",
                "source": "TOUCH",
            },
        )
    guard = 0
    while guard < 12:
        guard += 1
        q = client.post(f"/api/v1/sessions/{session_id}/ai/next-question").json()
        if q["completed"]:
            break
        raw = {"NUMBER": "8", "YES_NO": "YES", "SINGLE_CHOICE": "Getting Worse"}.get(
            q["question_type"], "no further detail"
        )
        client.post(
            f"/api/v1/sessions/{session_id}/ai/answer",
            json={
                "patient_id": patient_id,
                "question_id": q["question_id"],
                "raw_answer": raw,
                "answer_type": q["question_type"],
                "source": "TOUCH",
                **({} if q["question_id"] else {"asked_question_text": q["question"]}),
            },
        )


def _generate(client: TestClient, session_id: str, use_llm=False) -> dict:
    res = client.post(
        f"/api/v1/sessions/{session_id}/ai/summary",
        json={"use_llm_narrative": use_llm},
    )
    assert res.status_code == 200, res.text
    return res.json()


# ─── Historical fixture seeding (what Phase 6/7 will later write) ─────────────

def _seed_diabetes_history(patient_id: str) -> dict:
    """Previous prescription with Diabetes + Metformin, and a previous HbA1c report."""
    ids: dict[str, str] = {}
    with SessionLocal() as db:
        pres = Document(
            id=uuid.uuid4(),
            patient_id=uuid.UUID(patient_id),
            document_type=DocumentType.PRESCRIPTION.value,
            original_filename="prescription_2025.pdf",
            mime_type="application/pdf",
            file_size=12345,
            cloudinary_public_id="medikiosk/test/prescription_2025",
            cloudinary_resource_type="image",
            status="PROCESSED",
            document_date=utcnow() - timedelta(days=400),
            uploaded_at=utcnow() - timedelta(days=399),
        )
        db.add(pres)
        db.flush()
        db.add(
            DocumentExtraction(
                id=uuid.uuid4(),
                document_id=pres.id,
                diagnoses=[{"name": "Diabetes", "confidence": 0.94}],
                medications=[{"name": "Metformin", "dose": "500 mg", "confidence": 0.91}],
                status=ExtractionStatus.COMPLETED.value,
                overall_confidence=0.92,
                extraction_model="test-fixture",
            )
        )

        lab = Document(
            id=uuid.uuid4(),
            patient_id=uuid.UUID(patient_id),
            document_type=DocumentType.LAB_REPORT.value,
            original_filename="hba1c_2026.pdf",
            mime_type="application/pdf",
            file_size=2222,
            cloudinary_public_id="medikiosk/test/hba1c_2026",
            cloudinary_resource_type="image",
            status="PROCESSED",
            document_date=utcnow() - timedelta(days=200),
            uploaded_at=utcnow() - timedelta(days=199),
        )
        db.add(lab)
        db.flush()
        db.add(
            DocumentExtraction(
                id=uuid.uuid4(),
                document_id=lab.id,
                investigations=[
                    {"name": "HbA1c", "value": "8.2%", "date": "2026-02-12", "confidence": 0.96}
                ],
                status=ExtractionStatus.COMPLETED.value,
                overall_confidence=0.96,
                extraction_model="test-fixture",
            )
        )

        db.add(
            TimelineEvent(
                id=uuid.uuid4(),
                patient_id=uuid.UUID(patient_id),
                document_id=pres.id,
                event_type=TimelineEventType.DIAGNOSIS.value,
                event_date=date.today() - timedelta(days=400),
                title="Diabetes",
                description="Documented in an earlier prescription",
                source_type=InformationSource.DOCUMENT_OCR.value,
                source_id=pres.id,
                confidence=0.94,
            )
        )
        db.commit()
        ids["prescription_id"] = str(pres.id)
        ids["lab_id"] = str(lab.id)
    return ids


def _seed_vitals(session_id: str, patient_id: str) -> None:
    with SessionLocal() as db:
        db.add(
            Vital(
                id=uuid.uuid4(),
                session_id=uuid.UUID(session_id),
                patient_id=uuid.UUID(patient_id),
                weight_kg=62,
                height_cm=170,
                systolic_bp=150,
                diastolic_bp=90,
                pulse_bpm=88,
                temperature_c=37.2,
                spo2_percent=97,
                source=VitalSource.MANUAL.value,
                measured_at=utcnow(),
            )
        )
        db.commit()


def _seed_alert(session_id: str, patient_id: str) -> None:
    with SessionLocal() as db:
        db.add(
            Alert(
                id=uuid.uuid4(),
                session_id=uuid.UUID(session_id),
                patient_id=uuid.UUID(patient_id),
                alert_type=AlertType.ABNORMAL_VALUE.value,
                severity=AlertSeverity.MODERATE.value,
                title="Blood pressure above configured range",
                message="This response may require clinical review.",
                trigger_value={"systolic_bp": 150, "diastolic_bp": 90},
                status=AlertStatus.ACTIVE.value,
            )
        )
        db.commit()


def _values(items) -> list[str]:
    return [i["value"] for i in items]


# ═══ Scenario 1: patient WITH history ════════════════════════════════════════

def test_summary_separates_current_complaint_from_previous_history(client: TestClient):
    """The headline scenario: diabetes/Metformin/HbA1c history + today's complaint."""
    patient = _new_patient(client, "History Patient")
    _seed_diabetes_history(patient["id"])
    session_id = _new_session(client, patient)
    _seed_vitals(session_id, patient["id"])
    _seed_alert(session_id, patient["id"])
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)

    case = _generate(client, session_id)
    summary = case["summary"]
    current = summary["current_consultation"]
    history = summary["previous_history"]

    # ── CURRENT CONSULTATION ─────────────────────────────────────────────
    assert current["chief_complaint"]["value"] == "stomach pain"
    assert current["chief_complaint"]["source"] == InformationSource.PATIENT_INTERVIEW.value
    hpi = current["history_of_present_illness"]
    assert hpi["primary_complaint"]["value"] == "stomach pain"
    assert hpi["duration"]["value"] == "3 days"
    assert hpi["severity"]["value"] == "severe"
    assert _values(hpi["associated_symptoms"]) == ["vomiting"]
    assert hpi["associated_symptoms"][0]["detail"]["onset"] == "1 day"
    assert case["chief_complaint"] == "stomach pain"

    # Vitals + alerts belong to the current consultation.
    assert current["vitals"]["measurements"]["systolic_bp"] == 150
    assert current["vitals"]["source"] == InformationSource.VITAL_MEASUREMENT.value
    assert len(current["alerts"]) == 1
    assert current["alerts"][0]["alert_type"] == AlertType.ABNORMAL_VALUE.value

    # ── PREVIOUS HISTORY ─────────────────────────────────────────────────
    assert history["available"] is True
    assert "Diabetes" in _values(history["past_medical_history"])
    drug_values = " ".join(_values(history["drug_history"]))
    assert "Metformin" in drug_values
    assert "500 mg" in drug_values
    investigations = " ".join(_values(history["previous_investigations"]))
    assert "HbA1c" in investigations
    assert "8.2%" in investigations

    # Traceable to the originating document.
    diabetes = next(i for i in history["past_medical_history"] if i["value"] == "Diabetes")
    assert diabetes["source"] == InformationSource.DOCUMENT_OCR.value
    assert diabetes["source_ref"]["type"] in ("document", "timeline_event")
    assert diabetes["confidence"] == pytest.approx(0.94)

    # ── SEPARATION: history must not leak into the current block ──────────
    current_blob = str(current).lower()
    for term in ("diabetes", "metformin", "hba1c"):
        assert term not in current_blob, f"historical term '{term}' leaked into current_consultation"

    # ── NO CAUSALITY ─────────────────────────────────────────────────────
    text = case["summary_text"].lower()
    for phrase in (
        "caused by", "due to", "because of", "secondary to",
        "diabetes caused", "related to the", "consistent with",
    ):
        assert phrase not in text, f"summary asserts causality: '{phrase}'"
    assert "current consultation" in text
    assert "previous history" in text
    assert summary["safety"]["asserts_causality"] is False
    assert summary["safety"]["assembled_deterministically"] is True


def test_all_modern_medicine_sections_present(client: TestClient):
    """Every Modern Medicine section required by the requirement exists."""
    patient = _new_patient(client, "Sections Patient")
    _seed_diabetes_history(patient["id"])
    session_id = _new_session(client, patient)
    _seed_vitals(session_id, patient["id"])
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)

    summary = _generate(client, session_id)["summary"]
    current, history = summary["current_consultation"], summary["previous_history"]

    assert summary["workflow"]["summary_template"] == "MODERN_MEDICINE"
    # Chief Complaint, HPI, Review of Systems, Vitals -> current
    assert "chief_complaint" in current
    assert "history_of_present_illness" in current
    assert "review_of_systems" in current
    assert "vitals" in current
    # PMH, PSH, Drug, Allergy, Family, Personal, Previous Investigations -> history
    for section in MODERN_SECTIONS:
        assert section in history, f"missing section: {section}"
        assert isinstance(history[section], list)
    assert summary["ayush_assessment"] is None


# ═══ Scenario 2: brand-new patient, NO history ═══════════════════════════════

def test_new_patient_has_empty_history_and_no_fabrication(client: TestClient):
    patient = _new_patient(client, "Fresh Patient")
    session_id = _new_session(client, patient)
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)

    summary = _generate(client, session_id)["summary"]
    current, history = summary["current_consultation"], summary["previous_history"]

    # Current consultation is populated...
    assert current["chief_complaint"]["value"] == "stomach pain"
    assert current["interview_responses"]

    # ...and every historical section is genuinely empty, not invented.
    assert history["available"] is False
    for section in MODERN_SECTIONS:
        assert history[section] == [], f"{section} should be empty for a new patient"
    assert history["timeline"] == []
    assert history["previous_consultations"] == []
    assert history["sources_scanned"]["documents"] == 0
    assert history["sources_scanned"]["timeline_events"] == 0

    assert summary["data_availability"]["previous_history"] is False
    assert summary["data_availability"]["vitals"] is False

    text = summary_text = _generate(client, session_id)["summary_text"]
    assert "No previous records available" in summary_text
    for term in ("diabetes", "metformin", "hba1c", "hypertension"):
        assert term not in text.lower(), f"fabricated history: {term}"


# ═══ Scenario 3: multiple previous sessions ══════════════════════════════════

def test_multiple_previous_sessions_are_history_not_current(client: TestClient):
    """Prior sessions appear as previous consultations, never as today's answers."""
    patient = _new_patient(client, "Repeat Patient")

    # Two earlier consultations with different complaints.
    earlier_complaints = ["headache", "knee pain"]
    earlier_ids = []
    for complaint in earlier_complaints:
        prior_id = _new_session(client, patient)
        earlier_ids.append(prior_id)
        extraction = AnswerExtraction(
            primary_complaint=SymptomDetail(symptom=complaint, duration="2 days"),
            categories_satisfied=["CHIEF_COMPLAINT", "ONSET"],
            confidence=0.9,
        )
        with use_extraction(extraction):
            q = client.post(f"/api/v1/sessions/{prior_id}/ai/next-question").json()
            client.post(
                f"/api/v1/sessions/{prior_id}/ai/answer",
                json={
                    "patient_id": patient["id"],
                    "question_id": q["question_id"],
                    "raw_answer": f"I had {complaint}",
                    "answer_type": "TEXT",
                    "source": "TOUCH",
                },
            )

    # Today's session.
    session_id = _new_session(client, patient)
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)
    summary = _generate(client, session_id)["summary"]
    current, history = summary["current_consultation"], summary["previous_history"]

    # Today's complaint is the current one.
    assert current["chief_complaint"]["value"] == "stomach pain"
    assert current["session_id"] == session_id

    # Previous complaints are history, tagged with their own session ids.
    prior_values = [p["chief_complaint"] for p in history["previous_consultations"]]
    assert set(earlier_complaints) <= set(prior_values)
    assert "stomach pain" not in prior_values, "current session leaked into its own history"
    for entry in history["previous_consultations"]:
        assert entry["session_id"] != session_id
        assert entry["session_id"] in earlier_ids
        assert entry["source"] == InformationSource.PATIENT_INTERVIEW.value

    # CRITICAL: no earlier session's answer is present as a current interview response.
    current_answers = {r["answer"] for r in current["interview_responses"]}
    for complaint in earlier_complaints:
        assert f"I had {complaint}" not in current_answers
    for response in current["interview_responses"]:
        assert response["source_ref"]["session_id"] == session_id


def test_previous_session_answers_never_counted_as_current(client: TestClient):
    """Answer counts are scoped to the session under summary."""
    patient = _new_patient(client, "Scoping Patient")
    prior_id = _new_session(client, patient)
    _answer_interview(client, prior_id, patient["id"], "I had a cough for a week")

    session_id = _new_session(client, patient)
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)

    summary = _generate(client, session_id)["summary"]
    responses = summary["current_consultation"]["interview_responses"]

    with SessionLocal() as db:
        from app.models.answer import Answer
        from sqlalchemy import func, select as sa_select

        current_count = db.scalar(
            sa_select(func.count()).select_from(Answer).where(
                Answer.session_id == uuid.UUID(session_id)
            )
        )
    assert len(responses) == current_count
    assert all(r["source_ref"]["session_id"] == session_id for r in responses)


# ═══ AYUSH workflow ══════════════════════════════════════════════════════════

def test_ayush_summary_includes_ayush_assessment(client: TestClient):
    patient = _new_patient(client, "Ayurveda Patient")
    session_id = _new_session(client, patient, stream="AYUSH", dept="AYURVEDA")

    ayush_extraction = AnswerExtraction(
        primary_complaint=SymptomDetail(symptom="digestive discomfort", duration="1 week"),
        categories_satisfied=["CHIEF_COMPLAINT", "ONSET"],
        confidence=0.9,
    )
    _answer_interview_ayush(client, session_id, patient["id"], ayush_extraction)

    summary = _generate(client, session_id)["summary"]
    assert summary["workflow"]["summary_template"] == "AYUSH"
    assert summary["workflow"]["medical_stream_code"] == "AYUSH"
    ayush = summary["ayush_assessment"]
    assert ayush is not None
    categories = {f["category"] for f in ayush["findings"]}
    # The seeded AYUSH workflow collects Agni, Nidra and a Vata check.
    assert {"AGNI", "NIDRA", "VATA_CHECK"} & categories, categories
    # Modern-medicine historical sections still exist (empty for a new patient).
    for section in MODERN_SECTIONS:
        assert section in summary["previous_history"]


def _answer_interview_ayush(client, session_id, patient_id, extraction):
    with use_extraction(extraction):
        q = client.post(f"/api/v1/sessions/{session_id}/ai/next-question").json()
        client.post(
            f"/api/v1/sessions/{session_id}/ai/answer",
            json={
                "patient_id": patient_id,
                "question_id": q["question_id"],
                "raw_answer": "My digestion has been poor for a week",
                "answer_type": "TEXT",
                "source": "TOUCH",
            },
        )
    guard = 0
    while guard < 12:
        guard += 1
        q = client.post(f"/api/v1/sessions/{session_id}/ai/next-question").json()
        if q["completed"]:
            break
        raw = {"NUMBER": "6", "YES_NO": "NO"}.get(q["question_type"])
        if raw is None:
            opts = q.get("options")
            raw = opts[0] if isinstance(opts, list) and opts else "no further detail"
        client.post(
            f"/api/v1/sessions/{session_id}/ai/answer",
            json={
                "patient_id": patient_id,
                "question_id": q["question_id"],
                "raw_answer": raw,
                "answer_type": q["question_type"],
                "source": "TOUCH",
                **({} if q["question_id"] else {"asked_question_text": q["question"]}),
            },
        )


# ═══ Corrections and doctor verification ═════════════════════════════════════

def test_patient_correction_overrides_ai_draft(client: TestClient):
    patient = _new_patient(client, "Correcting Patient")
    session_id = _new_session(client, patient)
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)
    case = _generate(client, session_id)
    assert case["summary"]["current_consultation"]["chief_complaint"]["value"] == "stomach pain"

    res = client.post(
        f"/api/v1/cases/{case['id']}/edits",
        json={
            "field_name": "current_consultation.chief_complaint",
            "new_value": "lower abdominal pain",
            "reason": "Patient clarified the location",
            "editor_type": "PATIENT",
        },
    )
    assert res.status_code == 201, res.text
    assert res.json()["old_value"]["value"] == "stomach pain"

    updated = client.get(f"/api/v1/cases/{case['id']}").json()
    chief = updated["summary"]["current_consultation"]["chief_complaint"]
    assert chief["value"] == "lower abdominal pain"
    assert chief["source"] == InformationSource.PATIENT_CORRECTION.value
    corrections = updated["summary"]["patient_corrections"]
    assert len(corrections) == 1
    assert corrections[0]["field_name"] == "current_consultation.chief_complaint"
    assert corrections[0]["new_value"] == "lower abdominal pain"


def test_doctor_verified_field_survives_regeneration(client: TestClient):
    """AI regeneration must never silently overwrite doctor-verified data."""
    patient = _new_patient(client, "Doctor Verified Patient")
    session_id = _new_session(client, patient)
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)
    case = _generate(client, session_id)

    client.post(
        f"/api/v1/cases/{case['id']}/edits",
        json={
            "field_name": "current_consultation.history_of_present_illness.severity",
            "new_value": "moderate",
            "reason": "Clinician assessment",
            "editor_type": "DOCTOR",
        },
    )

    # Regenerate from scratch — the doctor's value must persist.
    regenerated = _generate(client, session_id)
    severity = regenerated["summary"]["current_consultation"]["history_of_present_illness"]["severity"]
    assert severity["value"] == "moderate"
    assert severity["source"] == InformationSource.DOCTOR_VERIFICATION.value
    assert (
        "current_consultation.history_of_present_illness.severity"
        in regenerated["summary"]["doctor_verified_fields"]
    )
    assert regenerated["status"] == CaseStatus.DOCTOR_VERIFIED.value


def test_doctor_correction_wins_over_patient_correction(client: TestClient):
    patient = _new_patient(client, "Both Editors Patient")
    session_id = _new_session(client, patient)
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)
    case = _generate(client, session_id)
    field = "current_consultation.chief_complaint"

    client.post(
        f"/api/v1/cases/{case['id']}/edits",
        json={"field_name": field, "new_value": "patient value", "editor_type": "PATIENT"},
    )
    client.post(
        f"/api/v1/cases/{case['id']}/edits",
        json={"field_name": field, "new_value": "doctor value", "editor_type": "DOCTOR"},
    )

    updated = client.get(f"/api/v1/cases/{case['id']}").json()
    chief = updated["summary"]["current_consultation"]["chief_complaint"]
    assert chief["value"] == "doctor value"
    assert chief["source"] == InformationSource.DOCTOR_VERIFICATION.value


def test_correction_to_unknown_field_rejected(client: TestClient):
    patient = _new_patient(client, "Bad Path Patient")
    session_id = _new_session(client, patient)
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)
    case = _generate(client, session_id)

    res = client.post(
        f"/api/v1/cases/{case['id']}/edits",
        json={"field_name": "previous_history.invented_section", "new_value": "x"},
    )
    assert res.status_code == 400
    assert "Unknown summary field" in res.json()["detail"]


# ═══ Case lifecycle / API ════════════════════════════════════════════════════

def test_one_case_per_session_and_regeneration_is_idempotent(client: TestClient):
    patient = _new_patient(client, "Idempotent Patient")
    session_id = _new_session(client, patient)
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)

    first = _generate(client, session_id)
    second = _generate(client, session_id)
    assert first["id"] == second["id"]

    with SessionLocal() as db:
        from sqlalchemy import func, select as sa_select

        count = db.scalar(
            sa_select(func.count()).select_from(Case).where(
                Case.session_id == uuid.UUID(session_id)
            )
        )
    assert count == 1

    fetched = client.get(f"/api/v1/sessions/{session_id}/ai/summary").json()
    assert fetched["id"] == first["id"]


def test_summary_before_generation_returns_404(client: TestClient):
    patient = _new_patient(client, "No Summary Patient")
    session_id = _new_session(client, patient)
    res = client.get(f"/api/v1/sessions/{session_id}/ai/summary")
    assert res.status_code == 404


def test_summary_for_unknown_session_returns_404(client: TestClient):
    res = client.post(f"/api/v1/sessions/{uuid.uuid4()}/ai/summary", json={})
    assert res.status_code == 404


def test_unknown_case_returns_404(client: TestClient):
    assert client.get(f"/api/v1/cases/{uuid.uuid4()}").status_code == 404


def test_patient_confirmed_session_advances_to_summary_generated(client: TestClient):
    """The state machine is respected: only PATIENT_CONFIRMED advances."""
    patient = _new_patient(client, "Confirmed Patient")
    session_id = _new_session(client, patient)
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)

    with SessionLocal() as db:
        session = db.get(IntakeSession, uuid.UUID(session_id))
        session.status = SessionStatus.PATIENT_CONFIRMED.value
        db.commit()

    case = _generate(client, session_id)
    assert case["status"] == CaseStatus.PATIENT_CONFIRMED.value
    session_after = client.get(f"/api/v1/sessions/{session_id}").json()
    assert session_after["status"] == SessionStatus.SUMMARY_GENERATED.value


# ═══ Narrative safety validators (deterministic) ═════════════════════════════

def test_narrative_validator_rejects_unsafe_text():
    from app.services.case import NarrativeRejected, validate_narrative

    assert validate_narrative("Chief complaint: stomach pain for 3 days.")

    unsafe = [
        "The stomach pain is due to the patient's diabetes.",
        "The pain is caused by the previous condition.",
        "This is consistent with a diabetic complication.",
        "The diagnosis is gastritis.",
        "The patient should take Metformin twice daily.",
        "We recommend starting antibiotics.",
        "The pain is secondary to diabetes.",
    ]
    for text in unsafe:
        with pytest.raises(NarrativeRejected):
            validate_narrative(text)

    with pytest.raises(NarrativeRejected):
        validate_narrative("")
    with pytest.raises(NarrativeRejected):
        validate_narrative("x" * 4000)

    # Internal identifiers must never reach doctor-facing prose.
    with pytest.raises(NarrativeRejected):
        validate_narrative(
            "Vitals recorded, vital_id 38c16efe-cf97-4a6c-985d-96d105811f3c."
        )
    with pytest.raises(NarrativeRejected):
        validate_narrative("Chief complaint: pain (source_ref: document).")


def test_llm_narrative_rejected_falls_back_to_deterministic(client: TestClient):
    """An unsafe LLM narrative is discarded, not stored."""
    patient = _new_patient(client, "Unsafe Narrative Patient")
    _seed_diabetes_history(patient["id"])
    session_id = _new_session(client, patient)
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)

    bad_llm = MagicMock()
    bad_llm.summarise_case.return_value = (
        "The patient's stomach pain is due to their long-standing diabetes."
    )
    with patch.object(settings, "OPENAI_API_KEY", "test-key"), \
         patch("app.services.llm.get_llm_service", return_value=bad_llm):
        case = _generate(client, session_id, use_llm=True)

    assert bad_llm.summarise_case.called
    assert case["summary"]["narrative_source"] == "deterministic"
    assert case["generated_by_model"] is None
    assert "due to" not in case["summary_text"].lower()


def test_llm_narrative_accepted_when_safe(client: TestClient):
    patient = _new_patient(client, "Safe Narrative Patient")
    session_id = _new_session(client, patient)
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)

    safe_text = (
        "CURRENT CONSULTATION The patient reports stomach pain for 3 days, "
        "described as severe, with vomiting starting 1 day ago. "
        "PREVIOUS HISTORY No previous records are available for this patient."
    )
    good_llm = MagicMock()
    good_llm.summarise_case.return_value = safe_text
    with patch.object(settings, "OPENAI_API_KEY", "test-key"), \
         patch.object(settings, "OPENAI_MODEL", "gpt-5-mini"), \
         patch("app.services.llm.get_llm_service", return_value=good_llm):
        case = _generate(client, session_id, use_llm=True)

    assert case["summary"]["narrative_source"] == "llm"
    assert case["generated_by_model"] == "gpt-5-mini"
    assert case["summary_text"] == safe_text


def test_llm_receives_only_structured_summary(client: TestClient):
    """The narrative model must never see raw patient answers directly."""
    patient = _new_patient(client, "Isolation Patient")
    session_id = _new_session(client, patient)
    _answer_interview(client, session_id, patient["id"], HINDI_ANSWER)

    llm = MagicMock()
    llm.summarise_case.return_value = "CURRENT CONSULTATION Reported stomach pain."
    with patch.object(settings, "OPENAI_API_KEY", "test-key"), \
         patch("app.services.llm.get_llm_service", return_value=llm):
        _generate(client, session_id, use_llm=True)

    (passed,), _ = llm.summarise_case.call_args
    assert isinstance(passed, dict)
    assert set(passed) >= {"current_consultation", "previous_history", "safety"}
    assert passed["safety"]["assembled_deterministically"] is True
