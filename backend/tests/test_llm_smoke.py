"""Live OpenAI smoke test (Phase 5B).

Behaviour required of this file:
  - No OPENAI_API_KEY configured  -> SKIPPED
  - Key configured                -> a real API call is made
  - API call fails                -> FAIL (loudly)

The v1 Gemini smoke test caught ``LLMUnavailableError`` and asserted on the
message, so it PASSED while the provider was completely broken. That is exactly
how a misconfigured model name stayed invisible. It must never happen again:
this test has no except branch.

Printing policy: enough to verify success, never the API key, never patient data.
The inputs below are synthetic, not real patient text.
"""
import uuid

import pytest

from app.core.config import settings

pytestmark = pytest.mark.skipif(
    not settings.llm_enabled,
    reason="OPENAI_API_KEY not configured — live smoke test skipped",
)

_ALLOWED = ["CHIEF_COMPLAINT", "ONSET", "SEVERITY", "FEVER_CHECK", "PROGRESSION"]


def test_live_openai_next_question_smoke():
    """Real API call for adaptive question selection. Any failure fails the test."""
    from app.services.llm import get_llm_service
    from app.services.llm.schemas import ClinicalContext, NextQuestionDecision

    ctx = ClinicalContext(
        session_id=str(uuid.uuid4()),
        language="en",
        medical_stream_code="MODERN_MEDICINE",
        department_code="GEN_MED",
        workflow_code="MOD_GEN_MED_V1",
        workflow_name="General Medicine Clinical Intake Workflow",
        answered_categories=["CHIEF_COMPLAINT"],
        satisfied_categories=["CHIEF_COMPLAINT", "ONSET", "SEVERITY"],
        remaining_categories=["FEVER_CHECK", "PROGRESSION"],
        known_facts={"symptom": "abdominal pain", "duration": "3 days", "severity": "severe"},
        recent_answers=[],
        total_questions=5,
        completed_questions=3,
        available_question_codes=["q_004", "q_005"],
    )

    # No try/except: a provider error must surface as a test failure.
    decision = get_llm_service().decide_next_question(ctx)

    print(f"\n[SMOKE] model            : {settings.OPENAI_MODEL}")
    print(f"[SMOKE] action           : {decision.action}")
    print(f"[SMOKE] question         : {decision.question}")
    print(f"[SMOKE] question_type    : {decision.question_type}")
    print(f"[SMOKE] question_code    : {decision.question_code}")
    print(f"[SMOKE] category         : {decision.category}")

    assert isinstance(decision, NextQuestionDecision)
    assert decision.action in ("ASK", "COMPLETE")
    if decision.action == "ASK":
        assert decision.question and 5 < len(decision.question) < 300
        assert decision.question_type in ("TEXT", "NUMBER", "YES_NO", "SINGLE_CHOICE")
        # Must not re-ask anything already satisfied.
        assert decision.category not in ("ONSET", "SEVERITY", "CHIEF_COMPLAINT"), (
            f"model proposed an already-satisfied category: {decision.category}"
        )
        if decision.question_code:
            assert decision.question_code in ctx.available_question_codes


def test_live_openai_multi_category_extraction_smoke():
    """Real API call for extraction. Verifies one answer -> several categories.

    Input is synthetic Hinglish text used purely as a regression fixture; it is
    not real patient data.
    """
    from app.services.llm import get_llm_service

    extraction = get_llm_service().extract_answer(
        raw_answer="Mujhe teen din se bahut tez pet dard hai",
        question_text="What is your primary health concern or symptom today?",
        question_type="TEXT",
        allowed_categories=_ALLOWED,
        question_category="CHIEF_COMPLAINT",
    )

    facts = extraction.facts_dict
    categories = set(extraction.categories_satisfied)
    print(f"\n[SMOKE] model            : {settings.OPENAI_MODEL}")
    print(f"[SMOKE] facts            : {facts}")
    print(f"[SMOKE] categories       : {sorted(categories)}")
    print(f"[SMOKE] confidence       : {extraction.bounded_confidence}")

    # Every returned category must come from the supplied vocabulary.
    assert categories <= set(_ALLOWED), f"model invented categories: {categories - set(_ALLOWED)}"

    # The sentence carries symptom + duration + severity, so all three
    # categories must be reported. This is the core Phase 5B behaviour.
    assert "CHIEF_COMPLAINT" in categories
    assert "ONSET" in categories, "duration ('teen din se' = 3 days) was not mapped to ONSET"
    assert "SEVERITY" in categories, "'bahut tez' (very intense) was not mapped to SEVERITY"

    joined = " ".join(f"{k}={v}" for k, v in facts.items()).lower()
    assert "pain" in joined or "abdominal" in joined or "stomach" in joined
    assert "3" in joined or "three" in joined
    assert extraction.bounded_confidence is None or 0.0 <= extraction.bounded_confidence <= 1.0
