"""Answer recording with bounded LLM extraction (Phase 5B).

Flow:
    1. Validate request / session / ownership
    2. Persist raw_answer immediately
    3. Attempt bounded-time LLM extraction (within LLM_TIMEOUT_SECONDS)
    4. If successful  -> persist structured facts + categories_satisfied + confidence
    5. If any failure -> raw_answer intact, no facts, confidence stays null
    6. Return response

The patient's answer is NEVER lost because the LLM provider is unavailable.
The kiosk NEVER blocks indefinitely.

PERSISTENCE SHAPE
    ``Answer.normalized_answer`` is JSONB, so the structured extraction is stored
    in-place under stable reserved keys rather than requiring a new migration:

        {
          "facts": {"symptom": "stomach pain", "duration": "3 days",
                    "severity": "severe"},
          "clinical": {
            "primary_complaint": {"symptom": "stomach pain", "duration": "3 days",
                                  "onset": null, "severity": "severe"},
            "associated_symptoms": [{"symptom": "vomiting", "onset": "1 day",
                                     "duration": null, "severity": null}],
            "progression": null
          },
          "categories_satisfied": ["CHIEF_COMPLAINT", "ONSET", "SEVERITY"],
          "raw_fallback": {"text": "<whatever the frontend sent>"},
          "ad_hoc_question": {"text": "...", "fingerprint": "..."}
        }

    ``facts`` is the FLAT view derived from the primary complaint plus any stated
    progression, and is what drives category-evidence checks. ``clinical`` keeps
    the full shape so an associated symptom's timing is never confused with the
    chief complaint's.

    ``raw_answer`` is written once and never touched again. The frontend's own
    normalized payload is preserved separately under ``raw_fallback`` so it can
    never be mistaken for LLM extraction — the previous implementation wrote it
    into the same slot, which made ``normalized_answer IS NOT NULL`` useless as a
    signal (it was non-null on 100% of rows while extraction had actually
    succeeded on under 5%). ``confidence`` remains the honest indicator: it is
    set only by a real extraction.
"""
from __future__ import annotations

import hashlib
import logging
import re
import uuid
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.answer import Answer
from app.models.clinical_workflow import ClinicalWorkflow
from app.models.intake_session import IntakeSession, SessionStatus
from app.models.question import Question
from app.schemas.answer import AnswerCreate, AnswerSubmissionResponse
from app.services.interview.clinical_facts import policy_for_workflow
from app.services.interview.workflow_service import WorkflowService
from app.services.llm.schemas import (
    AD_HOC_KEY,
    CATEGORIES_KEY,
    CLINICAL_KEY,
    FACTS_KEY,
    RAW_FALLBACK_KEY,
    AnswerExtraction,
)
from app.utils.datetime import utcnow

log = logging.getLogger(__name__)

# Answer types worth sending to the extractor. Closed-form types (NUMBER,
# YES_NO, SINGLE_CHOICE, MULTI_CHOICE) carry no free text to mine.
EXTRACTABLE_ANSWER_TYPES = frozenset({"TEXT", "VOICE"})

# Cap on the ad-hoc question text echoed back by the client and stored for
# de-duplication. Untrusted input: used for dedup only, never for category
# satisfaction.
MAX_AD_HOC_TEXT = 300

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")


def question_fingerprint(text: str) -> str:
    """Stable short fingerprint of a question, for repeat detection."""
    normalized = " ".join((text or "").lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


class AnswerService:

    @staticmethod
    def record_answer(
        db: Session,
        session_id: uuid.UUID,
        payload: AnswerCreate,
    ) -> AnswerSubmissionResponse:
        """Validate, persist raw answer, then attempt bounded LLM extraction."""

        # ── 1. Session validation ─────────────────────────────────────────
        session = db.get(IntakeSession, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Intake session with ID {session_id} not found",
            )

        if session.status == SessionStatus.CONSENT_GRANTED.value:
            session.status = SessionStatus.INTERVIEW_ACTIVE.value
            session.started_at = utcnow()
            db.commit()
            db.refresh(session)
        elif session.status != SessionStatus.INTERVIEW_ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot record answers on session with status "
                    f"'{session.status}'. Expected INTERVIEW_ACTIVE."
                ),
            )

        # ── 2. Patient ownership check ────────────────────────────────────
        patient_id = payload.patient_id or session.patient_id
        if session.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patient ID does not match session patient ID",
            )

        # ── 3. Resolve the session's workflow (scopes everything below) ────
        workflow: Optional[ClinicalWorkflow] = None
        if session.medical_stream_id:
            workflow = WorkflowService.get_active_workflow(
                db,
                medical_stream_id=session.medical_stream_id,
                department_id=session.department_id,
            )

        # ── 4. Validate question if provided ──────────────────────────────
        question: Optional[Question] = None
        if payload.question_id:
            question = db.get(Question, payload.question_id)
            if not question:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Question with ID {payload.question_id} not found",
                )
            if workflow is None or question.workflow_id != workflow.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Question does not belong to session's active clinical "
                        f"workflow '{workflow.name if workflow else 'unknown'}'"
                    ),
                )

        # ── 5. Persist raw answer immediately ─────────────────────────────
        # raw_answer is written once here and never modified again.
        ad_hoc_meta = AnswerService._build_ad_hoc_meta(payload, question)
        envelope: dict[str, Any] = {}
        if payload.normalized_answer:
            envelope[RAW_FALLBACK_KEY] = payload.normalized_answer
        if ad_hoc_meta:
            envelope[AD_HOC_KEY] = ad_hoc_meta

        now = utcnow()
        answer = Answer(
            id=uuid.uuid4(),
            session_id=session.id,
            question_id=payload.question_id,
            patient_id=session.patient_id,
            raw_answer=payload.raw_answer,
            normalized_answer=envelope or None,
            answer_type=payload.answer_type.upper(),
            source=payload.source.upper(),
            # Only a real extraction sets confidence; a client-supplied value is
            # not evidence of extraction.
            confidence=payload.confidence,
            answered_at=now,
            is_patient_corrected=payload.is_patient_corrected,
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)

        # ── 6. Bounded LLM extraction ─────────────────────────────────────
        allowed_categories = AnswerService._workflow_categories(db, workflow, session.language)
        should_extract = bool(
            settings.llm_enabled
            and payload.raw_answer
            and payload.raw_answer.strip()
            and payload.answer_type.upper() in EXTRACTABLE_ANSWER_TYPES
            and allowed_categories
        )

        if should_extract:
            question_text = (
                question.question_text
                if question is not None
                else (ad_hoc_meta or {}).get("text") or "Clinical intake follow-up question"
            )
            question_category = question.category if question is not None else None
            try:
                extraction = AnswerService._run_extraction(
                    raw_answer=payload.raw_answer,  # type: ignore[arg-type]
                    question_text=question_text,
                    question_type=payload.answer_type.upper(),
                    allowed_categories=allowed_categories,
                    question_category=question_category,
                )
                merged = AnswerService._merge_extraction(
                    envelope=dict(envelope),
                    extraction=extraction,
                    workflow=workflow,
                    allowed_categories=allowed_categories,
                    question_category=question_category,
                )
                answer.normalized_answer = merged
                answer.confidence = extraction.bounded_confidence
                # Committed here, before the client can issue the next
                # /ai/next-question request, so question selection always sees
                # the facts from the answer that preceded it.
                db.commit()
                db.refresh(answer)
                log.info(
                    "Answer extraction succeeded",
                    extra={
                        "session_id": str(session_id),
                        "question_id": str(payload.question_id),
                        "fact_count": len(merged.get(FACTS_KEY) or {}),
                        "categories_satisfied": merged.get(CATEGORIES_KEY),
                        "confidence": extraction.bounded_confidence,
                        "llm_success": True,
                    },
                )
            except Exception as exc:
                # ANY failure -> raw_answer preserved as-is, no fabricated facts,
                # confidence stays null. Log the exception CLASS only.
                db.rollback()
                log.info(
                    "Answer extraction failed — raw answer preserved",
                    extra={
                        "session_id": str(session_id),
                        "question_id": str(payload.question_id),
                        "error_class": type(exc).__name__,
                        "fallback_used": True,
                        "llm_success": False,
                    },
                )

        # ── 7. Is anything still worth asking? ────────────────────────────
        has_next = False
        try:
            from app.services.interview.question_service import QuestionService

            has_next = QuestionService.has_pending_questions(db, session.id)
        except Exception:
            has_next = False

        return AnswerSubmissionResponse(
            answer_id=answer.id,
            saved=True,
            next_question_available=has_next,
            message="Answer recorded successfully",
        )

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _build_ad_hoc_meta(
        payload: AnswerCreate, question: Optional[Question]
    ) -> Optional[dict[str, Any]]:
        """Record which LLM-generated question this answer belongs to.

        Only used when there is no DB question row. The text comes from the
        client and is therefore sanitized and length-capped; it drives repeat
        detection only. Category satisfaction is never taken from the client —
        it comes exclusively from server-side extraction.
        """
        if question is not None:
            return None
        text = sanitize_ad_hoc_text(payload.asked_question_text)
        if not text:
            return None
        return {"text": text, "fingerprint": question_fingerprint(text)}

    @staticmethod
    def _workflow_categories(
        db: Session, workflow: Optional[ClinicalWorkflow], language: Optional[str]
    ) -> list[str]:
        """Category vocabulary of the session's own workflow.

        Scoped to one workflow so facts and categories can never leak between
        hospitals, streams or departments.
        """
        if workflow is None:
            return []
        stmt = select(Question.category).where(
            Question.workflow_id == workflow.id,
            Question.category.is_not(None),
        )
        categories = {c for c in db.scalars(stmt).all() if c}
        return sorted(categories)

    @staticmethod
    def _merge_extraction(
        envelope: dict[str, Any],
        extraction: AnswerExtraction,
        workflow: Optional[ClinicalWorkflow],
        allowed_categories: list[str],
        question_category: Optional[str],
    ) -> dict[str, Any]:
        """Fold a successful extraction into the stored JSONB envelope."""
        policy = policy_for_workflow(workflow)

        # Flat map used for category-evidence checks and LLM context. Derived
        # from the PRIMARY complaint only — see AnswerExtraction.facts_dict.
        facts = extraction.facts_dict
        if facts:
            envelope[FACTS_KEY] = facts

        # Structured clinical shape: primary complaint vs associated symptoms,
        # each keeping its own timing. Stored alongside the flat map so nothing
        # is lost to flattening.
        if extraction.has_content:
            envelope[CLINICAL_KEY] = extraction.clinical_block

        # Only categories that exist in THIS workflow survive. The model cannot
        # invent a category and cannot reference another workflow's vocabulary.
        allowed_canonical = {policy.canonical(c): c for c in allowed_categories}
        accepted: set[str] = set()
        for raw in extraction.categories_satisfied:
            canonical = policy.canonical(raw)
            if canonical in allowed_canonical:
                accepted.add(allowed_canonical[canonical])

        # The question actually being answered is satisfied by definition.
        if question_category:
            accepted.add(question_category)

        if accepted:
            envelope[CATEGORIES_KEY] = sorted(accepted)
        return envelope

    @staticmethod
    def _run_extraction(
        raw_answer: str,
        question_text: str,
        question_type: str,
        allowed_categories: list[str],
        question_category: Optional[str],
    ) -> AnswerExtraction:
        """Run bounded LLM extraction. Raises LLMUnavailableError on failure."""
        from app.services.llm import get_llm_service

        llm = get_llm_service()
        return llm.extract_answer(
            raw_answer=raw_answer,
            question_text=question_text,
            question_type=question_type,
            allowed_categories=allowed_categories,
            question_category=question_category,
        )

    @staticmethod
    def get_session_answers(db: Session, session_id: uuid.UUID) -> list[Answer]:
        stmt = (
            select(Answer)
            .where(Answer.session_id == session_id)
            .order_by(Answer.answered_at.asc())
        )
        return list(db.scalars(stmt).all())


def sanitize_ad_hoc_text(text: Optional[str]) -> Optional[str]:
    """Sanitize a client-echoed ad-hoc question string for storage.

    Strips control characters, collapses whitespace and caps length. This value
    is stored for repeat detection only, so it is cleaned rather than rejected.
    """
    if not text:
        return None
    stripped = _CONTROL_CHARS_RE.sub(" ", str(text))
    collapsed = " ".join(stripped.split())[:MAX_AD_HOC_TEXT]
    return collapsed or None
