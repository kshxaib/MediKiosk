"""Adaptive Questioning Engine — Phase 5B (fact-aware, OpenAI + deterministic fallback).

THE BUG THIS FIXES
    v1 decided what was still needed from *which question rows had answers*:

        answered_categories = {q.category for q in questions if q.id in answered_ids}

    So "Mujhe teen din se bahut tez pet dard hai" (abdominal pain, 3 days,
    severe) answered q_001 and marked exactly one category — CHIEF_COMPLAINT.
    ONSET and SEVERITY were still reported as missing, and the engine asked for
    both. Structured extraction did happen, but its output was discarded and
    never reached question selection, so it could not help.

THE MODEL NOW
    A category is satisfied when EITHER its question has an answer row OR a
    previous answer's extracted facts covered it. One answer can therefore
    satisfy many categories.

    Every question is then classified into one of three tiers:

      SATISFIED  - category known AND the known value fits the question's type.
                   Skipped; counted as resolved so kiosk progress advances.
      REFINEMENT - category known but the value does not fit the question's
                   required shape. Qualitative "severe" satisfies the SEVERITY
                   category but is NOT a numeric 1-10 score, so instead of
                   re-asking the same question verbatim the patient is asked to
                   refine it, with their own words quoted back.
      PENDING    - genuinely missing. Asked first, in workflow sequence order.

    The backend, not the LLM, makes this call. Anything the model proposes is
    re-checked against the same tiers and rejected if it targets a satisfied
    category — including a reworded duplicate, because comparison is on the
    canonical category, not the question text.

MULTI-HOSPITAL SAFETY
    Questions come only from the session's own resolved workflow, and facts only
    from the session's own answer rows. Nothing crosses hospital, stream,
    department or workflow boundaries.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.answer import Answer
from app.models.clinical_workflow import ClinicalWorkflow
from app.models.department import Department
from app.models.intake_session import IntakeSession, SessionStatus
from app.models.medical_stream import MedicalStream
from app.models.question import Question
from app.schemas.question import NextQuestionResponse
from app.services.interview.clinical_facts import (
    ClinicalPolicy,
    build_refinement_question,
    policy_for_workflow,
)
from app.services.interview.workflow_service import WorkflowService
from app.services.llm.schemas import (
    AD_HOC_KEY,
    CATEGORIES_KEY,
    CLINICAL_KEY,
    FACTS_KEY,
    PROHIBITED_KEYWORDS,
)
from app.utils.datetime import utcnow

log = logging.getLogger(__name__)

MAX_GENERATED_QUESTION_LENGTH = 300


def _contains_prohibited(text: str) -> bool:
    """Shared with the LLM service validator (single keyword source of truth)."""
    lower = text.lower()
    return any(kw in lower for kw in PROHIBITED_KEYWORDS)


def classify_questions(
    questions: list[Question],
    answered_ids: set[uuid.UUID],
    satisfied_canonical: set[str],
    known_facts: dict[str, Any],
    policy: ClinicalPolicy,
) -> tuple[list[Question], list[tuple[Question, str]], list[Question]]:
    """Sort unanswered questions into (pending, refinements, skipped).

    Pure function so the tiering rules can be tested without a database.

      pending     - category genuinely missing; ask it.
      refinements - category known, but the known value does not fit the shape
                    this question requires (e.g. qualitative "severe" for a
                    numeric 1-10 field). Ask the patient to refine, quoting
                    their own words, rather than repeating the question.
      skipped     - category known and the value fits; do not ask. Counted as
                    resolved so kiosk progress advances.
    """
    pending: list[Question] = []
    refinements: list[tuple[Question, str]] = []
    skipped: list[Question] = []

    for question in questions:
        if question.id in answered_ids:
            continue
        canonical = policy.canonical(question.category)
        if not canonical or canonical not in satisfied_canonical:
            pending.append(question)
            continue
        known_value = policy.fact_value_for_category(known_facts, question.category)
        if policy.is_value_sufficient(question, known_value):
            skipped.append(question)
        else:
            refinements.append((question, known_value or ""))

    return pending, refinements, skipped


@dataclass
class InterviewState:
    """Everything needed to choose the next question, computed once per request."""

    session: IntakeSession
    workflow: ClinicalWorkflow
    policy: ClinicalPolicy
    language: str
    questions: list[Question]
    answered_ids: set[uuid.UUID]
    # Categories whose own question has an answer row.
    answered_categories: set[str]
    # Union of answered_categories and categories covered by extracted facts.
    satisfied_canonical: set[str]
    known_facts: dict[str, Any]
    answers: list[Answer]
    ad_hoc_answer_count: int
    ad_hoc_fingerprints: set[str]
    ad_hoc_texts: list[str]
    pending: list[Question]
    refinements: list[tuple[Question, str]]
    skipped: list[Question]

    @property
    def total_questions(self) -> int:
        return len(self.questions) + self.ad_hoc_answer_count

    @property
    def completed_questions(self) -> int:
        answered_in_workflow = sum(1 for q in self.questions if q.id in self.answered_ids)
        return answered_in_workflow + len(self.skipped) + self.ad_hoc_answer_count

    @property
    def satisfied_labels(self) -> list[str]:
        """Human-readable satisfied categories, using this workflow's spellings."""
        labels: dict[str, str] = {}
        for q in self.questions:
            canonical = self.policy.canonical(q.category)
            if canonical and canonical in self.satisfied_canonical and q.category:
                labels[canonical] = q.category
        for canonical in self.satisfied_canonical:
            labels.setdefault(canonical, canonical)
        return sorted(labels.values())

    @property
    def remaining_labels(self) -> list[str]:
        seen: dict[str, str] = {}
        for q in self.pending:
            if q.category:
                seen.setdefault(self.policy.canonical(q.category) or q.category, q.category)
        return sorted(seen.values())


class QuestionService:
    # ── Public entry points ─────────────────────────────────────────────────

    @staticmethod
    def get_next_question_adaptive(db: Session, session_id: uuid.UUID) -> NextQuestionResponse:
        """Adaptive entry point: try the LLM, fall back to deterministic.

        Both paths enforce the same known-facts rules, so an LLM outage can never
        reintroduce a question whose category is already satisfied.
        """
        state = QuestionService._load_state(db, session_id)

        if settings.llm_enabled:
            try:
                return QuestionService._llm_question(state)
            except Exception as exc:
                log.info(
                    "LLM next-question failed — using deterministic fallback",
                    extra={
                        "session_id": str(session_id),
                        "error_class": type(exc).__name__,
                        "fallback_used": True,
                    },
                )
        return QuestionService._deterministic_question(state, llm_used=False)

    @staticmethod
    def get_next_question(db: Session, session_id: uuid.UUID) -> NextQuestionResponse:
        """Deterministic next-question — always safe, and fact-aware."""
        state = QuestionService._load_state(db, session_id)
        return QuestionService._deterministic_question(state, llm_used=False)

    @staticmethod
    def has_pending_questions(db: Session, session_id: uuid.UUID) -> bool:
        """True when anything is still worth asking (pending or refinement)."""
        try:
            state = QuestionService._load_state(db, session_id, activate=False)
        except HTTPException:
            return False
        return bool(state.pending or state.refinements)

    # ── State assembly ──────────────────────────────────────────────────────

    @staticmethod
    def _load_state(
        db: Session, session_id: uuid.UUID, activate: bool = True
    ) -> InterviewState:
        session = db.get(IntakeSession, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Intake session with ID {session_id} not found",
            )

        if activate:
            if session.status == SessionStatus.CONSENT_GRANTED.value:
                session.status = SessionStatus.INTERVIEW_ACTIVE.value
                session.started_at = utcnow()
                db.commit()
                db.refresh(session)
            elif session.status != SessionStatus.INTERVIEW_ACTIVE.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Cannot retrieve next question for session with status "
                        f"'{session.status}'. Expected INTERVIEW_ACTIVE."
                    ),
                )

        if not session.medical_stream_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session does not have a medical stream selected.",
            )

        workflow = WorkflowService.get_active_workflow(
            db,
            medical_stream_id=session.medical_stream_id,
            department_id=session.department_id,
        )
        policy = policy_for_workflow(workflow)
        language = session.language or "en"
        questions = QuestionService._fetch_workflow_questions(db, workflow.id, language)

        answers = list(
            db.scalars(
                select(Answer)
                .where(Answer.session_id == session.id)
                .order_by(Answer.answered_at.asc())
            ).all()
        )

        answered_ids = {a.question_id for a in answers if a.question_id is not None}
        by_id = {q.id: q for q in questions}

        # Categories satisfied because their own question was answered.
        answered_categories: set[str] = set()
        for qid in answered_ids:
            question = by_id.get(qid)
            canonical = policy.canonical(question.category) if question else None
            if canonical:
                answered_categories.add(canonical)

        # Categories satisfied because a previous answer's facts covered them,
        # plus the merged fact map for the whole session.
        known_facts: dict[str, Any] = {}
        extracted_categories: set[str] = set()
        ad_hoc_fingerprints: set[str] = set()
        ad_hoc_texts: list[str] = []
        ad_hoc_answer_count = 0

        for answer in answers:
            envelope = answer.normalized_answer or {}
            if not isinstance(envelope, dict):
                continue
            facts = envelope.get(FACTS_KEY)
            if isinstance(facts, dict):
                known_facts.update({str(k): v for k, v in facts.items()})
                for key in facts:
                    extracted_categories |= policy.categories_for_fact_key(str(key))
            categories = envelope.get(CATEGORIES_KEY)
            if isinstance(categories, list):
                extracted_categories |= policy.canonical_set(categories)
            if answer.question_id is None:
                ad_hoc_answer_count += 1
                ad_hoc = envelope.get(AD_HOC_KEY)
                if isinstance(ad_hoc, dict):
                    fingerprint = ad_hoc.get("fingerprint")
                    text = ad_hoc.get("text")
                    if fingerprint:
                        ad_hoc_fingerprints.add(str(fingerprint))
                    if text:
                        ad_hoc_texts.append(str(text))

        # Only categories that exist in THIS workflow can be satisfied, so an
        # extractor slip can never mark an unrelated slot done.
        workflow_canonical = {
            policy.canonical(q.category) for q in questions if q.category
        }
        workflow_canonical.discard(None)

        # An extractor may LIST a category it merely inferred. Require a backing
        # fact value, otherwise the category stays genuinely missing. Without
        # this, "with vomiting since yesterday" was enough for the model to claim
        # PROGRESSION even though the patient never said whether the condition
        # was improving or worsening — the question then got demoted to the
        # refinement tier and asked out of order.
        substantiated = {
            category
            for category in extracted_categories
            if policy.is_category_substantiated(known_facts, category)
        }
        if substantiated != extracted_categories:
            log.info(
                "Dropped unsubstantiated extracted categories",
                extra={
                    "session_id": str(session.id),
                    "dropped": sorted(extracted_categories - substantiated),
                },
            )

        # Categories answered directly need no fact evidence — the patient
        # answered that question.
        satisfied_canonical = (
            answered_categories | (substantiated & workflow_canonical)  # type: ignore[operator]
        )

        pending, refinements, skipped = classify_questions(
            questions=questions,
            answered_ids=answered_ids,
            satisfied_canonical=satisfied_canonical,  # type: ignore[arg-type]
            known_facts=known_facts,
            policy=policy,
        )

        return InterviewState(
            session=session,
            workflow=workflow,
            policy=policy,
            language=language,
            questions=questions,
            answered_ids=answered_ids,
            answered_categories=answered_categories,
            satisfied_canonical=satisfied_canonical,  # type: ignore[arg-type]
            known_facts=known_facts,
            answers=answers,
            ad_hoc_answer_count=ad_hoc_answer_count,
            ad_hoc_fingerprints=ad_hoc_fingerprints,
            ad_hoc_texts=ad_hoc_texts,
            pending=pending,
            refinements=refinements,
            skipped=skipped,
        )

    # ── Deterministic engine ────────────────────────────────────────────────

    @staticmethod
    def _deterministic_question(
        state: InterviewState, llm_used: bool
    ) -> NextQuestionResponse:
        """Fact-aware deterministic selection.

        Unlike v1 this is NOT "first unanswered by sequence" — questions whose
        information is already known are skipped, and partially-known ones are
        deferred to a refinement pass so genuinely missing information is
        collected first.
        """
        if not state.questions:
            return NextQuestionResponse(
                completed=True,
                total_questions=0,
                completed_questions=0,
                message=f"No questions configured for workflow '{state.workflow.name}'",
                llm_used=llm_used,
            )

        if state.pending:
            question = state.pending[0]
            return QuestionService._db_question_response(
                state,
                question,
                reason=(question.category or "clinical_assessment").lower(),
                llm_used=llm_used,
            )

        if state.refinements:
            question, known_value = state.refinements[0]
            return QuestionService._refinement_response(
                state, question, known_value, llm_used=llm_used
            )

        return QuestionService._completed_response(state, llm_used=llm_used)

    # ── LLM engine ──────────────────────────────────────────────────────────

    @staticmethod
    def _llm_question(state: InterviewState) -> NextQuestionResponse:
        """Ask the LLM, then re-validate its proposal against known facts."""
        from app.services.llm import get_llm_service
        from app.services.llm.schemas import ClinicalContext, PreviousAnswerSummary

        if not state.pending and not state.refinements:
            return QuestionService._completed_response(state, llm_used=False)

        by_id = {q.id: q for q in state.questions}
        recent_summaries: list[PreviousAnswerSummary] = []
        for answer in state.answers[-10:]:
            question = by_id.get(answer.question_id) if answer.question_id else None
            envelope = answer.normalized_answer or {}
            facts = envelope.get(FACTS_KEY) if isinstance(envelope, dict) else None
            categories = envelope.get(CATEGORIES_KEY) if isinstance(envelope, dict) else None
            clinical = envelope.get(CLINICAL_KEY) if isinstance(envelope, dict) else None
            associated = clinical.get("associated_symptoms") if isinstance(clinical, dict) else None
            include_raw = answer.answer_type.upper() in ("TEXT", "NUMBER", "VOICE")
            question_text = "Clinical intake follow-up question"
            if question is not None:
                question_text = question.question_text
            elif isinstance(envelope, dict) and isinstance(envelope.get(AD_HOC_KEY), dict):
                question_text = str(envelope[AD_HOC_KEY].get("text") or question_text)
            recent_summaries.append(
                PreviousAnswerSummary(
                    category=question.category if question else None,
                    question_code=question.question_code if question else None,
                    question_text=question_text,
                    answer_type=answer.answer_type,
                    raw_answer=answer.raw_answer if include_raw else None,
                    facts=facts if isinstance(facts, dict) else {},
                    categories_satisfied=categories if isinstance(categories, list) else [],
                    associated_symptoms=(
                        [s for s in associated if isinstance(s, dict)]
                        if isinstance(associated, list)
                        else []
                    ),
                )
            )

        stream_code = "UNKNOWN"
        dept_code = "UNKNOWN"
        db = Session.object_session(state.session)
        if db is not None:
            if state.session.medical_stream_id:
                stream_obj = db.get(MedicalStream, state.session.medical_stream_id)
                if stream_obj:
                    stream_code = stream_obj.code
            if state.session.department_id:
                dept_obj = db.get(Department, state.session.department_id)
                if dept_obj:
                    dept_code = dept_obj.code

        ctx = ClinicalContext(
            session_id=str(state.session.id),
            language=state.language,
            medical_stream_code=stream_code,
            department_code=dept_code,
            workflow_code=state.workflow.code,
            workflow_name=state.workflow.name,
            answered_categories=sorted(state.answered_categories),
            satisfied_categories=state.satisfied_labels,
            remaining_categories=state.remaining_labels,
            known_facts=state.known_facts,
            recent_answers=recent_summaries,
            total_questions=state.total_questions,
            completed_questions=state.completed_questions,
            # Only genuinely-missing questions are offered to the model.
            available_question_codes=[q.question_code for q in state.pending],
            previously_generated_questions=state.ad_hoc_texts,
        )

        decision = get_llm_service().decide_next_question(ctx)

        # ── COMPLETE: backend verifies independently ─────────────────────
        if decision.action == "COMPLETE":
            required_outstanding = [
                q for q in state.pending + [r[0] for r in state.refinements] if q.is_required
            ]
            if required_outstanding or state.pending or state.refinements:
                log.info(
                    "LLM suggested COMPLETE but backend check failed — continuing",
                    extra={"session_id": str(state.session.id)},
                )
                return QuestionService._deterministic_question(state, llm_used=True)
            return QuestionService._completed_response(state, llm_used=True)

        # ── ASK with an existing question code ───────────────────────────
        if decision.question_code:
            matched = next(
                (q for q in state.pending if q.question_code == decision.question_code),
                None,
            )
            if matched:
                return QuestionService._db_question_response(
                    state,
                    matched,
                    reason=decision.reason or (matched.category or "clinical_assessment"),
                    llm_used=True,
                )
            # The code is unknown, already answered, or already satisfied.
            # Rejected — do not serve it.
            log.info(
                "Rejected LLM question_code — not in the pending pool",
                extra={
                    "session_id": str(state.session.id),
                    "question_code": decision.question_code,
                    "rejection": "code_not_pending",
                },
            )
            return QuestionService._deterministic_question(state, llm_used=True)

        # ── ASK with a generated question: full backend validation ────────
        rejection = QuestionService._reject_generated_question(state, decision)
        if rejection:
            log.info(
                "Rejected LLM-generated question",
                extra={
                    "session_id": str(state.session.id),
                    "category": decision.category,
                    "rejection": rejection,
                },
            )
            return QuestionService._deterministic_question(state, llm_used=True)

        q_text = (decision.question or "").strip()
        q_type = (decision.question_type or "TEXT").upper()
        if q_type not in ("TEXT", "NUMBER", "YES_NO", "SINGLE_CHOICE"):
            q_type = "TEXT"

        return NextQuestionResponse(
            question_id=None,  # LLM-generated: no DB row
            question=q_text,
            question_type=q_type,
            required=False,
            reason=decision.reason or decision.category,
            category=decision.category,
            options=None,
            sequence=None,
            total_questions=state.total_questions,
            completed_questions=state.completed_questions,
            is_last_question=False,
            completed=False,
            llm_used=True,
            satisfied_categories=state.satisfied_labels,
            is_refinement=False,
        )

    @staticmethod
    def _reject_generated_question(
        state: InterviewState, decision: Any
    ) -> Optional[str]:
        """Return a rejection reason for a generated question, or None to allow.

        This is the backend's duplicate protection. It does not trust the model
        to have honoured the prompt.
        """
        q_text = (decision.question or "").strip()
        if not q_text:
            return "empty_question"
        if len(q_text) > MAX_GENERATED_QUESTION_LENGTH:
            return "too_long"
        if _contains_prohibited(q_text):
            return "prohibited_content"

        # Category-level duplicate: a reworded question targeting a satisfied
        # category is still a duplicate, because comparison is canonical.
        canonical = state.policy.canonical(decision.category)
        if canonical and canonical in state.satisfied_canonical:
            return "category_already_satisfied"

        # A generated question that merely restates a pending DB question's
        # category is allowed (it may be better worded), but one whose category
        # is not in the workflow at all is only allowed when it is genuinely new.
        from app.services.interview.answer_service import question_fingerprint

        if question_fingerprint(q_text) in state.ad_hoc_fingerprints:
            return "already_asked_ad_hoc"

        # Guard against asking for a fact we already hold, even if the model
        # labelled the category differently or omitted it.
        if state.known_facts:
            inferred = set()
            for token in q_text.lower().replace("?", " ").split():
                inferred |= state.policy.categories_for_fact_key(token)
            if inferred and inferred <= state.satisfied_canonical:
                return "asks_for_known_facts"

        return None

    # ── Response builders ───────────────────────────────────────────────────

    @staticmethod
    def _db_question_response(
        state: InterviewState,
        question: Question,
        reason: Optional[str],
        llm_used: bool,
    ) -> NextQuestionResponse:
        outstanding = len(state.pending) + len(state.refinements)
        return NextQuestionResponse(
            question_id=str(question.id),
            question=question.question_text,
            question_type=question.question_type.upper(),
            required=question.is_required,
            reason=reason,
            category=question.category,
            options=question.options,
            sequence=question.sequence,
            total_questions=state.total_questions,
            completed_questions=state.completed_questions,
            is_last_question=outstanding <= 1,
            completed=False,
            llm_used=llm_used,
            satisfied_categories=state.satisfied_labels,
            is_refinement=False,
        )

    @staticmethod
    def _refinement_response(
        state: InterviewState,
        question: Question,
        known_value: str,
        llm_used: bool,
    ) -> NextQuestionResponse:
        """Ask the patient to refine a partially-known answer.

        The question keeps its real question_id, so answering it counts toward
        progress and marks the category answered exactly like a normal answer.
        """
        outstanding = len(state.pending) + len(state.refinements)
        return NextQuestionResponse(
            question_id=str(question.id),
            question=build_refinement_question(question.question_text, known_value),
            question_type=question.question_type.upper(),
            required=question.is_required,
            reason="refine_known_value",
            category=question.category,
            options=question.options,
            sequence=question.sequence,
            total_questions=state.total_questions,
            completed_questions=state.completed_questions,
            is_last_question=outstanding <= 1,
            completed=False,
            llm_used=llm_used,
            satisfied_categories=state.satisfied_labels,
            is_refinement=True,
        )

    @staticmethod
    def _completed_response(state: InterviewState, llm_used: bool) -> NextQuestionResponse:
        return NextQuestionResponse(
            completed=True,
            total_questions=state.total_questions,
            completed_questions=state.completed_questions,
            is_last_question=True,
            message="All clinical intake questions have been completed.",
            llm_used=llm_used,
            satisfied_categories=state.satisfied_labels,
        )

    # ── Shared helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _fetch_workflow_questions(
        db: Session, workflow_id: uuid.UUID, lang: str
    ) -> list[Question]:
        stmt = (
            select(Question)
            .where(Question.workflow_id == workflow_id, Question.language == lang)
            .order_by(Question.sequence.asc())
        )
        questions = list(db.scalars(stmt).all())
        if not questions and lang != "en":
            stmt_en = (
                select(Question)
                .where(Question.workflow_id == workflow_id, Question.language == "en")
                .order_by(Question.sequence.asc())
            )
            questions = list(db.scalars(stmt_en).all())
        return questions
