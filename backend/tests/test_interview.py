"""Phase 5A + 5B clinical interview tests.

Phase 5A behaviour (workflow/question/answer plumbing, ownership, lifecycle) is
preserved. Phase 5B adds the fact-aware adaptive engine, so the expectations
around question ORDER changed: a question whose information the session already
has must no longer be asked.

Note on ``test_answer_submission_and_skipping_answered``: the pre-fix version of
that test asserted the bug. It answered the chief-complaint question with
"Severe headache and dull pain behind the eyes for two days" — which contains
the duration — and then required the ONSET question to be asked next. It has
been rewritten below (``test_next_question_after_first_answer_*``) to assert the
corrected behaviour instead.
"""
import random
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import create_app
from app.services.llm.schemas import (
    AnswerExtraction,
    ExtractedFact,
    NextQuestionDecision,
    SymptomDetail,
)

HINDI_ANSWER = "Mujhe teen din se bahut tez pet dard hai"


def random_mobile() -> str:
    return f"9{random.randint(100000000, 999999999)}"


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


# ─── LLM stubbing helpers ─────────────────────────────────────────────────────

def _fake_llm(extraction=None, decision=None):
    """A BaseLLMService stand-in. No network, deterministic."""
    svc = MagicMock()
    if extraction is None:
        from app.services.llm.base import LLMUnavailableError

        svc.extract_answer.side_effect = LLMUnavailableError("extraction disabled in test")
    else:
        svc.extract_answer.return_value = extraction
    if decision is None:
        from app.services.llm.base import LLMUnavailableError

        svc.decide_next_question.side_effect = LLMUnavailableError("no LLM in test")
    else:
        svc.decide_next_question.return_value = decision
    return svc


def use_llm(extraction=None, decision=None):
    """Context manager: enable the LLM path with a stubbed service."""
    from contextlib import ExitStack

    stack = ExitStack()
    stack.enter_context(patch.object(settings, "OPENAI_API_KEY", "test-key"))
    stack.enter_context(
        patch("app.services.llm.get_llm_service", return_value=_fake_llm(extraction, decision))
    )
    return stack


MULTI_CATEGORY_EXTRACTION = AnswerExtraction(
    primary_complaint=SymptomDetail(
        symptom="stomach pain", duration="3 days", severity="severe"
    ),
    categories_satisfied=["CHIEF_COMPLAINT", "ONSET", "SEVERITY"],
    confidence=0.95,
)


# ─── Session bootstrap ────────────────────────────────────────────────────────

def _new_session(client: TestClient, stream_code="MODERN_MEDICINE", dept_code="GEN_MED") -> dict:
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

    streams = client.get("/api/v1/streams").json()
    stream = next(s for s in streams if s["code"] == stream_code)
    depts = client.get(f"/api/v1/departments?stream_code={stream_code}").json()
    dept = next(d for d in depts if d["code"] == dept_code)

    res_sess = client.post(
        "/api/v1/sessions",
        json={
            "patient_id": patient["id"],
            "medical_stream_id": stream["id"],
            "department_id": dept["id"],
            "language": "en",
        },
    )
    assert res_sess.status_code == 201
    session = res_sess.json()

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
        "stream": stream,
        "department": dept,
    }


@pytest.fixture
def initialized_session(client: TestClient) -> dict:
    return _new_session(client)


def _answer(client, session_id, patient_id, question_id, raw, answer_type="TEXT", **extra):
    payload = {
        "patient_id": patient_id,
        "question_id": question_id,
        "raw_answer": raw,
        "answer_type": answer_type,
        "source": "TOUCH",
        **extra,
    }
    return client.post(f"/api/v1/sessions/{session_id}/ai/answer", json=payload)


def _next(client, session_id):
    res = client.post(f"/api/v1/sessions/{session_id}/ai/next-question")
    assert res.status_code == 200, res.text
    return res.json()


# ═══ Phase 5A regression (unchanged behaviour) ════════════════════════════════

def test_get_stream_workflows(client: TestClient, initialized_session: dict):
    stream_id = initialized_session["stream"]["id"]
    res = client.get(f"/api/v1/streams/{stream_id}/workflows")
    assert res.status_code == 200
    workflows = res.json()
    assert len(workflows) >= 1
    assert any(w["code"] == "MOD_GEN_MED_V1" for w in workflows)


def test_first_question_retrieval(client: TestClient, initialized_session: dict):
    data = _next(client, initialized_session["session_id"])
    assert data["completed"] is False
    assert data["question_id"] is not None
    assert "primary health concern" in data["question"].lower()
    assert data["question_type"] == "TEXT"
    assert data["required"] is True
    assert data["sequence"] == 1
    assert data["total_questions"] >= 5
    assert data["completed_questions"] == 0
    assert data["is_refinement"] is False


def test_answer_patient_ownership_mismatch_rejected(client: TestClient, initialized_session: dict):
    """#17 — session ownership is still enforced."""
    session_id = initialized_session["session_id"]
    q_id = _next(client, session_id)["question_id"]
    res = _answer(client, session_id, str(uuid.uuid4()), q_id, "Should fail")
    assert res.status_code == 403


def test_answer_invalid_question_id_rejected(client: TestClient, initialized_session: dict):
    session_id = initialized_session["session_id"]
    res = _answer(
        client, session_id, initialized_session["patient"]["id"],
        str(uuid.uuid4()), "Invalid question ID",
    )
    assert res.status_code == 404


def test_ayush_workflow_questions_retrieval(client: TestClient):
    """Multi-stream safety: the AYUSH session gets AYUSH questions only."""
    ctx = _new_session(client, stream_code="AYUSH", dept_code="AYURVEDA")
    data = _next(client, ctx["session_id"])
    assert data["question_id"] is not None
    assert "imbalance" in data["question"].lower()
    assert data["total_questions"] >= 4


def test_full_question_lifecycle_to_completion(client: TestClient, initialized_session: dict):
    """Phase 5A lifecycle still terminates. Runs with the LLM disabled."""
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    guard = 0
    while guard < 20:
        guard += 1
        q = _next(client, session_id)
        if q["completed"]:
            break
        q_type = q["question_type"]
        raw = {"NUMBER": "7", "YES_NO": "YES", "SINGLE_CHOICE": "Getting Worse"}.get(
            q_type, "Started yesterday morning"
        )
        res = _answer(client, session_id, patient_id, q["question_id"], raw, answer_type=q_type)
        assert res.status_code == 201
    assert guard < 20, "interview did not terminate"

    final = _next(client, session_id)
    assert final["completed"] is True
    answers = client.get(f"/api/v1/sessions/{session_id}/answers").json()
    assert len(answers) >= 5


# ═══ Phase 5B — the core bug ══════════════════════════════════════════════════

def test_multi_category_answer_satisfies_three_categories(
    client: TestClient, initialized_session: dict
):
    """#1 #2 #3 #7 #13 #14 — one answer covering symptom + duration + severity.

    Replaces the old ``test_answer_submission_and_skipping_answered``, which
    required ONSET to be asked next even though the answer contained a duration.
    """
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    with use_llm(extraction=MULTI_CATEGORY_EXTRACTION):
        q1 = _next(client, session_id)
        assert q1["category"] == "CHIEF_COMPLAINT"

        res = _answer(
            client, session_id, patient_id, q1["question_id"], HINDI_ANSWER,
            normalized_answer={"text": HINDI_ANSWER},
        )
        assert res.status_code == 201
        assert res.json()["saved"] is True

        # #13 — facts and categories persisted; #14 — raw answer intact.
        stored = client.get(f"/api/v1/sessions/{session_id}/answers").json()
        row = next(a for a in stored if a["question_id"] == q1["question_id"])
        assert row["raw_answer"] == HINDI_ANSWER
        assert row["normalized_answer"]["facts"] == {
            "symptom": "stomach pain",
            "duration": "3 days",
            "severity": "severe",
        }
        assert set(row["normalized_answer"]["categories_satisfied"]) == {
            "CHIEF_COMPLAINT", "ONSET", "SEVERITY",
        }
        # The frontend's own payload is preserved separately, never mistaken
        # for extraction output.
        assert row["normalized_answer"]["raw_fallback"] == {"text": HINDI_ANSWER}
        assert row["confidence"] == pytest.approx(0.95)

        # #2 — ONSET must NOT be asked again, in any wording.
        q2 = _next(client, session_id)
        assert q2["completed"] is False
        assert q2["category"] != "ONSET"
        assert "when did this symptom" not in q2["question"].lower()
        assert set(q2["satisfied_categories"]) >= {"CHIEF_COMPLAINT", "ONSET", "SEVERITY"}
        # #3 — the qualitative duration satisfied the TEXT-typed ONSET question,
        # so it was skipped entirely and counted as resolved: 1 answered (q_001)
        # + 1 skipped (q_002/ONSET) = 2. SEVERITY is deliberately NOT counted
        # here because it is numeric and still needs refinement.
        assert q2["completed_questions"] == 2


def test_numeric_severity_triggers_refinement_not_repeat(
    client: TestClient, initialized_session: dict
):
    """#4 — qualitative "severe" must not be treated as a numeric 1-10 answer.

    The seeded SEVERITY question is NUMBER with min 1 / max 10, so the engine
    asks for a numeric refinement that quotes the patient back, instead of
    silently skipping or blindly repeating the question.
    """
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    with use_llm(extraction=MULTI_CATEGORY_EXTRACTION):
        q1 = _next(client, session_id)
        _answer(client, session_id, patient_id, q1["question_id"], HINDI_ANSWER)

        # Walk to the end; SEVERITY must appear exactly once, as a refinement.
        severity_prompts = []
        guard = 0
        while guard < 20:
            guard += 1
            q = _next(client, session_id)
            if q["completed"]:
                break
            if q["category"] == "SEVERITY":
                severity_prompts.append(q)
            q_type = q["question_type"]
            raw = {"NUMBER": "8", "YES_NO": "NO", "SINGLE_CHOICE": "Getting Worse"}.get(
                q_type, "no further detail"
            )
            _answer(client, session_id, patient_id, q["question_id"], raw, answer_type=q_type)

    assert len(severity_prompts) == 1, "severity was asked more than once"
    prompt = severity_prompts[0]
    assert prompt["is_refinement"] is True
    assert prompt["reason"] == "refine_known_value"
    assert 'You mentioned it is "severe"' in prompt["question"]
    assert "scale of 1" in prompt["question"].lower()
    # It keeps the real question_id so it counts toward progress.
    assert prompt["question_id"] is not None


def test_deterministic_fallback_skips_satisfied_categories(
    client: TestClient, initialized_session: dict
):
    """#11 #12 — with the LLM dead, satisfied categories still must not return.

    This is the exact failure mode from the manual report: extraction had
    succeeded earlier in the session, then the provider went down, and the
    deterministic engine walked the workflow in sequence order and re-asked
    ONSET.
    """
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    # Turn 1: extraction works.
    with use_llm(extraction=MULTI_CATEGORY_EXTRACTION):
        q1 = _next(client, session_id)
        _answer(client, session_id, patient_id, q1["question_id"], HINDI_ANSWER)

    # Turn 2: provider is completely unavailable (no key at all).
    q2 = _next(client, session_id)
    assert q2["llm_used"] is False
    assert q2["completed"] is False
    assert q2["category"] != "ONSET"
    assert q2["category"] != "CHIEF_COMPLAINT"
    assert set(q2["satisfied_categories"]) >= {"CHIEF_COMPLAINT", "ONSET", "SEVERITY"}


def test_missing_information_still_produces_a_question(
    client: TestClient, initialized_session: dict
):
    """#5 — genuinely missing categories are still asked."""
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    with use_llm(extraction=MULTI_CATEGORY_EXTRACTION):
        q1 = _next(client, session_id)
        _answer(client, session_id, patient_id, q1["question_id"], HINDI_ANSWER)
        q2 = _next(client, session_id)

    # FEVER_CHECK and PROGRESSION were never covered by the answer.
    assert q2["completed"] is False
    assert q2["category"] in ("FEVER_CHECK", "PROGRESSION")
    assert q2["question"]


def test_backend_rejects_llm_duplicate_with_different_wording(
    client: TestClient, initialized_session: dict
):
    """#6 #10 — a reworded question targeting a satisfied category is rejected.

    "How long have you had this pain?" is DURATION, which canonicalises to
    ONSET. The backend must refuse it even though the wording and the category
    label both differ from the original question.
    """
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    reworded = NextQuestionDecision(
        action="ASK",
        question="How long have you had this pain?",
        question_type="TEXT",
        question_code=None,
        category="DURATION",
        reason="trying to re-ask onset",
    )

    with use_llm(extraction=MULTI_CATEGORY_EXTRACTION):
        q1 = _next(client, session_id)
        _answer(client, session_id, patient_id, q1["question_id"], HINDI_ANSWER)

    with use_llm(decision=reworded):
        q2 = _next(client, session_id)

    assert q2["llm_used"] is True  # the LLM ran...
    assert "how long have you had this pain" not in q2["question"].lower()  # ...and was overruled
    assert q2["category"] != "ONSET"


def test_backend_rejects_llm_question_code_for_satisfied_category(
    client: TestClient, initialized_session: dict
):
    """#10 — even a valid pool code is refused once its category is satisfied."""
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    with use_llm(extraction=MULTI_CATEGORY_EXTRACTION):
        q1 = _next(client, session_id)
        _answer(client, session_id, patient_id, q1["question_id"], HINDI_ANSWER)

    # q_002 is the ONSET question — already satisfied by extracted facts.
    with use_llm(decision=NextQuestionDecision(
        action="ASK", question="When did this start?", question_type="TEXT",
        question_code="q_002", category="ONSET",
    )):
        q2 = _next(client, session_id)

    assert q2["category"] != "ONSET"
    assert "when did this symptom or discomfort start" not in q2["question"].lower()


def test_llm_complete_too_early_is_overridden(client: TestClient, initialized_session: dict):
    """The backend, not the LLM, decides when the interview is done."""
    session_id = initialized_session["session_id"]

    with use_llm(decision=NextQuestionDecision(action="COMPLETE", reason="looks done to me")):
        q = _next(client, session_id)

    assert q["completed"] is False
    assert q["question_id"] is not None


def test_extraction_failure_preserves_raw_answer(client: TestClient, initialized_session: dict):
    """#15 — a dead extractor must not lose the answer or invent facts."""
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    # extraction=None -> the stub raises LLMUnavailableError.
    with use_llm(extraction=None):
        q1 = _next(client, session_id)
        res = _answer(
            client, session_id, patient_id, q1["question_id"], HINDI_ANSWER,
            normalized_answer={"text": HINDI_ANSWER},
        )
        assert res.status_code == 201

    stored = client.get(f"/api/v1/sessions/{session_id}/answers").json()
    row = next(a for a in stored if a["question_id"] == q1["question_id"])
    assert row["raw_answer"] == HINDI_ANSWER          # never lost
    assert row["confidence"] is None                   # honest signal
    envelope = row["normalized_answer"] or {}
    assert "facts" not in envelope                     # nothing fabricated
    assert "categories_satisfied" not in envelope
    assert envelope.get("raw_fallback") == {"text": HINDI_ANSWER}

    # And with no facts, the engine correctly still asks about onset.
    q2 = _next(client, session_id)
    assert q2["category"] == "ONSET"


def test_facts_survive_database_reload(client: TestClient, initialized_session: dict):
    """#7 — normalized facts are readable from a fresh DB session."""
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    with use_llm(extraction=MULTI_CATEGORY_EXTRACTION):
        q1 = _next(client, session_id)
        _answer(client, session_id, patient_id, q1["question_id"], HINDI_ANSWER)

    from app.db.session import SessionLocal
    from app.services.interview.question_service import QuestionService

    with SessionLocal() as fresh_db:
        state = QuestionService._load_state(fresh_db, uuid.UUID(session_id), activate=False)
        # #8 / #9 — state carries known_facts and satisfied categories.
        assert state.known_facts["duration"] == "3 days"
        assert state.known_facts["severity"] == "severe"
        assert {"CHIEF_COMPLAINT", "ONSET", "SEVERITY"} <= state.satisfied_canonical
        assert "ONSET" not in [q.category for q in state.pending]
        assert any(q.category == "SEVERITY" for q, _ in state.refinements)
        assert any(q.category == "ONSET" for q in state.skipped)


def test_clinical_context_contains_known_facts_and_satisfied(
    client: TestClient, initialized_session: dict
):
    """#8 #9 — the ClinicalContext handed to the LLM carries facts + categories."""
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    with use_llm(extraction=MULTI_CATEGORY_EXTRACTION):
        q1 = _next(client, session_id)
        _answer(client, session_id, patient_id, q1["question_id"], HINDI_ANSWER)

    stub = _fake_llm(decision=NextQuestionDecision(
        action="ASK", question="Do you have a fever?", question_type="YES_NO",
        question_code="q_004", category="FEVER_CHECK",
    ))
    with patch.object(settings, "OPENAI_API_KEY", "test-key"), \
         patch("app.services.llm.get_llm_service", return_value=stub):
        _next(client, session_id)

    ctx = stub.decide_next_question.call_args[0][0]
    assert ctx.known_facts["symptom"] == "stomach pain"
    assert ctx.known_facts["duration"] == "3 days"
    assert {"CHIEF_COMPLAINT", "ONSET", "SEVERITY"} <= set(ctx.satisfied_categories)
    assert "ONSET" not in ctx.remaining_categories
    assert "q_002" not in ctx.available_question_codes  # satisfied -> withheld
    assert "q_004" in ctx.available_question_codes
    assert ctx.workflow_code == "MOD_GEN_MED_V1"


def test_ad_hoc_llm_question_does_not_stall_or_repeat(
    client: TestClient, initialized_session: dict
):
    """#16 — an LLM-generated question with no question_id must not loop.

    v1 stored such answers with question_id NULL, so they never entered the
    answered set: progress froze and the same generated question could be
    proposed forever.
    """
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    generated = NextQuestionDecision(
        action="ASK",
        question="Has anything you tried made the discomfort better or worse?",
        question_type="TEXT",
        question_code=None,
        category="AGGRAVATING_FACTORS",
        reason="useful follow-up",
    )

    with use_llm(decision=generated):
        first = _next(client, session_id)
        assert first["question_id"] is None
        assert first["question"] == generated.question
        progress_before = first["completed_questions"]

        # Answer it, echoing the question text back as the kiosk now does.
        res = _answer(
            client, session_id, patient_id, None,
            "Eating makes it worse",
            asked_question_text=generated.question,
        )
        assert res.status_code == 201

        # Progress advanced despite question_id being NULL.
        second = _next(client, session_id)
        assert second["completed_questions"] > progress_before
        # ...and the identical generated question is not served again.
        assert second["question"] != generated.question

    stored = client.get(f"/api/v1/sessions/{session_id}/answers").json()
    ad_hoc = next(a for a in stored if a["question_id"] is None)
    assert ad_hoc["raw_answer"] == "Eating makes it worse"
    assert ad_hoc["normalized_answer"]["ad_hoc_question"]["text"] == generated.question
    assert ad_hoc["normalized_answer"]["ad_hoc_question"]["fingerprint"]


def test_facts_do_not_leak_between_sessions(client: TestClient):
    """#14 (multi-hospital safety) — one patient's facts never affect another."""
    first = _new_session(client)
    second = _new_session(client)

    with use_llm(extraction=MULTI_CATEGORY_EXTRACTION):
        q1 = _next(client, first["session_id"])
        _answer(client, first["session_id"], first["patient"]["id"], q1["question_id"], HINDI_ANSWER)

    # The second, untouched session must still start from the beginning.
    fresh = _next(client, second["session_id"])
    assert fresh["category"] == "CHIEF_COMPLAINT"
    assert fresh["completed_questions"] == 0
    assert fresh["satisfied_categories"] == []


def test_extracted_categories_outside_workflow_are_dropped(
    client: TestClient, initialized_session: dict
):
    """An extractor cannot mark a category this workflow does not define."""
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]

    rogue = AnswerExtraction(
        primary_complaint=SymptomDetail(symptom="stomach pain"),
        # NIDRA belongs to the AYUSH workflow, not this one.
        categories_satisfied=["CHIEF_COMPLAINT", "NIDRA", "TOTALLY_MADE_UP"],
        confidence=0.9,
    )
    with use_llm(extraction=rogue):
        q1 = _next(client, session_id)
        _answer(client, session_id, patient_id, q1["question_id"], HINDI_ANSWER)

    stored = client.get(f"/api/v1/sessions/{session_id}/answers").json()
    row = next(a for a in stored if a["question_id"] == q1["question_id"])
    assert set(row["normalized_answer"]["categories_satisfied"]) == {"CHIEF_COMPLAINT"}


# ═══ Extraction shape: primary vs associated symptoms ════════════════════════

# The five scenarios required as regressions. Each entry is
# (label, patient answer, expected extraction) — expectations mirror what the
# live model actually returns for these inputs, verified against gpt-5-mini.
SYMPTOM_SCENARIOS = [
    (
        "pain_only",
        "have severe stomach pain for 3 days",
        AnswerExtraction(
            primary_complaint=SymptomDetail(
                symptom="stomach pain", duration="3 days", severity="severe"
            ),
            categories_satisfied=["CHIEF_COMPLAINT", "ONSET", "SEVERITY"],
            confidence=0.95,
        ),
    ),
    (
        "pain_plus_vomiting",
        "have severe stomach pain for 3 days, with vomiting since yesterday",
        AnswerExtraction(
            primary_complaint=SymptomDetail(
                symptom="stomach pain", duration="3 days", severity="severe"
            ),
            associated_symptoms=[SymptomDetail(symptom="vomiting", onset="1 day")],
            categories_satisfied=["CHIEF_COMPLAINT", "ONSET", "SEVERITY"],
            confidence=0.95,
        ),
    ),
    (
        "headache_plus_fever",
        "headache for 2 days and fever since last night",
        AnswerExtraction(
            primary_complaint=SymptomDetail(symptom="headache", duration="2 days"),
            associated_symptoms=[SymptomDetail(symptom="fever", onset="1 day")],
            categories_satisfied=["CHIEF_COMPLAINT", "ONSET", "FEVER_CHECK"],
            confidence=0.93,
        ),
    ),
    (
        "cough_worsening",
        "cough for one week and it is getting worse",
        AnswerExtraction(
            primary_complaint=SymptomDetail(symptom="cough", duration="1 week"),
            progression="worsening",
            categories_satisfied=["CHIEF_COMPLAINT", "ONSET", "PROGRESSION"],
            confidence=0.94,
        ),
    ),
    (
        "vomiting_only",
        "vomiting since yesterday",
        AnswerExtraction(
            primary_complaint=SymptomDetail(symptom="vomiting", onset="1 day"),
            categories_satisfied=["CHIEF_COMPLAINT", "ONSET"],
            confidence=0.92,
        ),
    ),
]


@pytest.mark.parametrize(
    "label,raw,extraction", SYMPTOM_SCENARIOS, ids=[s[0] for s in SYMPTOM_SCENARIOS]
)
def test_primary_complaint_stays_primary(client: TestClient, label, raw, extraction):
    """The primary complaint is never displaced by a later/associated symptom.

    Regression: for "severe stomach pain for 3 days, with vomiting since
    yesterday" the flat-bag schema stored symptom="vomiting" while the pain
    survived only as a bare duration and severity.
    """
    ctx = _new_session(client)
    session_id, patient_id = ctx["session_id"], ctx["patient"]["id"]

    with use_llm(extraction=extraction):
        q1 = _next(client, session_id)
        res = _answer(
            client, session_id, patient_id, q1["question_id"], raw,
            normalized_answer={"text": raw},
        )
        assert res.status_code == 201

    stored = client.get(f"/api/v1/sessions/{session_id}/answers").json()
    row = next(a for a in stored if a["question_id"] == q1["question_id"])
    env = row["normalized_answer"]

    assert row["raw_answer"] == raw
    expected_primary = extraction.primary_complaint

    # Flat view: the PRIMARY symptom, never an associated one.
    assert env["facts"]["symptom"] == expected_primary.symptom
    # Structured view keeps the full shape.
    clinical = env["clinical"]
    assert clinical["primary_complaint"]["symptom"] == expected_primary.symptom
    assert clinical["primary_complaint"]["duration"] == expected_primary.duration
    assert clinical["primary_complaint"]["onset"] == expected_primary.onset
    assert clinical["primary_complaint"]["severity"] == expected_primary.severity

    # Associated symptoms keep their OWN timing.
    assert clinical["associated_symptoms"] == [
        s.model_dump() for s in extraction.associated_symptoms
    ]

    # Progression is only present when the patient stated a direction.
    assert clinical["progression"] == extraction.progression
    if extraction.progression is None:
        assert "progression" not in env["facts"], (
            f"{label}: progression must not be inferred from a time expression"
        )
    else:
        assert env["facts"]["progression"] == extraction.progression


def test_associated_symptom_timing_does_not_satisfy_onset(client: TestClient):
    """An associated symptom's onset must not date the chief complaint.

    "stomach pain, with vomiting since yesterday" says nothing about when the
    PAIN started, so ONSET must remain pending.
    """
    ctx = _new_session(client)
    session_id, patient_id = ctx["session_id"], ctx["patient"]["id"]
    raw = "stomach pain, with vomiting since yesterday"

    undated_primary = AnswerExtraction(
        primary_complaint=SymptomDetail(symptom="stomach pain"),   # no duration/onset
        associated_symptoms=[SymptomDetail(symptom="vomiting", onset="1 day")],
        categories_satisfied=["CHIEF_COMPLAINT"],
        confidence=0.9,
    )

    with use_llm(extraction=undated_primary):
        q1 = _next(client, session_id)
        _answer(client, session_id, patient_id, q1["question_id"], raw)

    from app.db.session import SessionLocal
    from app.services.interview.question_service import QuestionService

    with SessionLocal() as db:
        state = QuestionService._load_state(db, uuid.UUID(session_id), activate=False)

    assert "ONSET" not in state.satisfied_canonical
    assert "q_002" in [q.question_code for q in state.pending]
    # The associated symptom is still on record, just not used to date the pain.
    stored = client.get(f"/api/v1/sessions/{session_id}/answers").json()
    env = next(a for a in stored if a["question_id"] == q1["question_id"])["normalized_answer"]
    assert env["clinical"]["associated_symptoms"][0]["symptom"] == "vomiting"

    # And the kiosk correctly asks when the pain started.
    nxt = _next(client, session_id)
    assert nxt["category"] == "ONSET"


def test_stated_progression_satisfies_progression_category(client: TestClient):
    """A stated direction of change DOES satisfy PROGRESSION (and skips it)."""
    ctx = _new_session(client)
    session_id, patient_id = ctx["session_id"], ctx["patient"]["id"]

    _, raw, extraction = SYMPTOM_SCENARIOS[3]  # cough_worsening
    with use_llm(extraction=extraction):
        q1 = _next(client, session_id)
        _answer(client, session_id, patient_id, q1["question_id"], raw)

    from app.db.session import SessionLocal
    from app.services.interview.question_service import QuestionService

    with SessionLocal() as db:
        state = QuestionService._load_state(db, uuid.UUID(session_id), activate=False)

    assert "PROGRESSION" in state.satisfied_canonical
    assert "q_005" in [q.question_code for q in state.skipped]
    assert "q_002" in [q.question_code for q in state.skipped]   # ONSET: "1 week"
    # No severity was stated, so SEVERITY stays genuinely missing.
    assert "SEVERITY" not in state.satisfied_canonical
    assert "q_003" in [q.question_code for q in state.pending]


def test_associated_symptoms_reach_the_question_engine(client: TestClient):
    """Associated symptoms must be visible to question selection, not just stored.

    Storing data the engine never reads is the exact failure class that caused
    the original bug, so guard against reintroducing it.
    """
    ctx = _new_session(client)
    session_id, patient_id = ctx["session_id"], ctx["patient"]["id"]
    _, raw, extraction = SYMPTOM_SCENARIOS[1]  # pain_plus_vomiting

    with use_llm(extraction=extraction):
        q1 = _next(client, session_id)
        _answer(client, session_id, patient_id, q1["question_id"], raw)

    stub = _fake_llm(decision=NextQuestionDecision(
        action="ASK", question="Do you have a fever?", question_type="YES_NO",
        question_code="q_004", category="FEVER_CHECK",
    ))
    with patch.object(settings, "OPENAI_API_KEY", "test-key"), \
         patch("app.services.llm.get_llm_service", return_value=stub):
        _next(client, session_id)

    llm_ctx = stub.decide_next_question.call_args[0][0]
    summary = llm_ctx.recent_answers[-1]
    assert summary.associated_symptoms[0]["symptom"] == "vomiting"
    assert summary.facts["symptom"] == "stomach pain"

    from app.services.llm.openai_service import OpenAIService

    rendered = OpenAIService._build_next_question_user_message(llm_ctx)
    assert "also reported" in rendered
    assert "vomiting" in rendered


# ═══ Pure tiering logic (no database) ═════════════════════════════════════════

def _q(code, category, qtype, *, options=None, rules=None, required=True):
    return MagicMock(
        id=uuid.uuid4(), question_code=code, category=category, question_type=qtype,
        options=options, validation_rules=rules, is_required=required,
        question_text=f"{code} text",
    )


def test_classification_tiers():
    """#3 vs #4 — the skip / refine distinction, isolated from the database."""
    from app.services.interview.clinical_facts import DEFAULT_POLICY
    from app.services.interview.question_service import classify_questions

    onset_text = _q("q_002", "ONSET", "TEXT")
    severity_number = _q("q_003", "SEVERITY", "NUMBER", rules={"min": 1, "max": 10})
    severity_text = _q("q_003b", "SEVERITY", "TEXT")
    fever = _q("q_004", "FEVER_CHECK", "YES_NO", options=["YES", "NO"])

    pending, refinements, skipped = classify_questions(
        questions=[onset_text, severity_number, severity_text, fever],
        answered_ids=set(),
        satisfied_canonical={"CHIEF_COMPLAINT", "ONSET", "SEVERITY"},
        known_facts={"duration": "3 days", "severity": "severe"},
        policy=DEFAULT_POLICY,
    )

    # ONSET: qualitative "3 days" fits a TEXT question -> skipped.
    # SEVERITY as TEXT: qualitative "severe" fits -> skipped.
    assert {q.question_code for q in skipped} == {"q_002", "q_003b"}
    # SEVERITY as NUMBER: "severe" is not a 1-10 score -> refinement.
    assert [q.question_code for q, _ in refinements] == ["q_003"]
    assert refinements[0][1] == "severe"
    # FEVER_CHECK: never satisfied -> pending.
    assert [q.question_code for q in pending] == ["q_004"]


def test_classification_ignores_answered_questions():
    from app.services.interview.clinical_facts import DEFAULT_POLICY
    from app.services.interview.question_service import classify_questions

    answered = _q("q_001", "CHIEF_COMPLAINT", "TEXT")
    other = _q("q_004", "FEVER_CHECK", "YES_NO", options=["YES", "NO"])
    pending, refinements, skipped = classify_questions(
        questions=[answered, other],
        answered_ids={answered.id},
        satisfied_canonical={"CHIEF_COMPLAINT"},
        known_facts={},
        policy=DEFAULT_POLICY,
    )
    assert [q.question_code for q in pending] == ["q_004"]
    assert refinements == [] and skipped == []


def test_unsubstantiated_category_claim_is_not_trusted(
    client: TestClient, initialized_session: dict
):
    """Regression from a live kiosk session.

    For "have severe stomach pain for 3 days, with vomiting since yesterday" the
    extractor listed PROGRESSION as satisfied, but the patient never said whether
    the condition was improving or worsening and no fact backed the claim. The
    engine trusted it, found no usable value, and demoted PROGRESSION to the
    refinement tier — so it was queued behind the severity refinement instead of
    being asked as genuinely missing information.

    An extracted category claim with no supporting fact must be dropped.
    """
    session_id = initialized_session["session_id"]
    patient_id = initialized_session["patient"]["id"]
    raw = "have severe stomach pain for 3 days, with vomiting since yesterday"

    over_claiming = AnswerExtraction(
        primary_complaint=SymptomDetail(
            symptom="stomach pain", duration="3 days", severity="severe"
        ),
        associated_symptoms=[SymptomDetail(symptom="vomiting", onset="1 day")],
        # PROGRESSION is claimed but no progression/trend/course fact supports it.
        categories_satisfied=["CHIEF_COMPLAINT", "ONSET", "PROGRESSION", "SEVERITY"],
        confidence=0.95,
    )

    with use_llm(extraction=over_claiming):
        q1 = _next(client, session_id)
        _answer(client, session_id, patient_id, q1["question_id"], raw)

    from app.db.session import SessionLocal
    from app.services.interview.question_service import QuestionService

    with SessionLocal() as db:
        state = QuestionService._load_state(db, uuid.UUID(session_id), activate=False)

    # Backed by facts -> genuinely satisfied.
    assert {"CHIEF_COMPLAINT", "ONSET", "SEVERITY"} <= state.satisfied_canonical
    # Claimed without evidence -> dropped, so it stays genuinely missing.
    assert "PROGRESSION" not in state.satisfied_canonical
    pending_codes = [q.question_code for q in state.pending]
    assert "q_005" in pending_codes                     # PROGRESSION: still to ask
    assert "q_004" in pending_codes                     # FEVER_CHECK: never claimed
    # PROGRESSION must be PENDING, not demoted to the refinement tier.
    assert [q.question_code for q, _ in state.refinements] == ["q_003"]
    assert [q.question_code for q in state.skipped] == ["q_002"]

    # Genuinely-missing questions are asked before any refinement, in workflow
    # sequence order, and PROGRESSION is among them rather than queued behind.
    nxt = _next(client, session_id)
    assert nxt["is_refinement"] is False
    assert nxt["category"] in ("FEVER_CHECK", "PROGRESSION")
