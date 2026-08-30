"""Structured AI Case Summary assembly (Phase 5C).

    Patient Interview + Vitals + Previous Documents + Timeline
    + Patient Corrections + Alerts
                  |
        deterministic assembly (this module)
                  |
        Case.summary  (structured JSONB - authoritative)
                  |
        optional LLM narrative -> Case.summary_text

DESIGN RULES
    1. Assembly is 100% deterministic. No LLM is involved in producing the
       structured summary, so it cannot contain invented facts.
    2. Phase 5B structured facts are REUSED. raw_answer is never re-extracted.
    3. Current session and history are assembled from disjoint queries and live
       in separate top-level blocks. Historical data never populates a
       current-consultation field, and no causal link between them is expressed.
    4. Missing data yields empty lists / nulls plus a data_availability report.
       Nothing is fabricated.
    5. Every item carries a `source` from InformationSource and a `source_ref`.
    6. Correction precedence: AI draft -> PATIENT corrections -> DOCTOR
       corrections. Doctor-verified fields are re-applied on every regeneration
       so AI can never silently overwrite them (§33).
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.alert import Alert, AlertStatus
from app.models.answer import Answer
from app.models.case import Case, CaseEdit, CaseStatus, EditorType
from app.models.intake_session import IntakeSession, SessionStatus
from app.models.question import Question
from app.models.timeline_event import InformationSource
from app.models.vital import Vital
from app.services.case.historical_context import HistoricalContextService, history_item
from app.services.case.narrative import (
    NarrativeRejected,
    build_deterministic_narrative,
    validate_narrative,
)
from app.services.interview.clinical_facts import policy_for_workflow
from app.services.interview.workflow_service import WorkflowService
from app.services.llm.schemas import CATEGORIES_KEY, CLINICAL_KEY, FACTS_KEY
from app.utils.datetime import utcnow

log = logging.getLogger(__name__)

SUMMARY_SCHEMA_VERSION = "5c.1"

AYUSH_STREAM_CODE = "AYUSH"

# Canonical categories that belong to the history of present illness rather than
# to the generic review-of-systems list.
_HPI_CATEGORIES = frozenset({"CHIEF_COMPLAINT", "ONSET", "SEVERITY", "PROGRESSION"})

# AYUSH assessment categories (populated only for the AYUSH workflow).
_AYUSH_CATEGORIES = frozenset({"AGNI", "NIDRA", "VATA_CHECK", "PITTA_CHECK", "KAPHA_CHECK"})

_VITAL_FIELDS = (
    "weight_kg",
    "height_cm",
    "systolic_bp",
    "diastolic_bp",
    "pulse_bpm",
    "temperature_c",
    "spo2_percent",
)


def _clean(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = " ".join(str(value).split())
    return text or None


def _get_path(data: dict[str, Any], dotted: str) -> Any:
    node: Any = data
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _set_path(data: dict[str, Any], dotted: str, value: Any) -> bool:
    """Set a dotted path inside the summary. Returns False if the path is absent.

    Only paths that already exist in the generated structure may be corrected, so
    a correction cannot invent a new section.
    """
    parts = dotted.split(".")
    node: Any = data
    for part in parts[:-1]:
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    if not isinstance(node, dict) or parts[-1] not in node:
        return False
    node[parts[-1]] = value
    return True


class CaseSummaryService:
    """Builds and persists the structured case summary for one intake session."""

    # ── Public API ────────────────────────────────────────────────────────

    @staticmethod
    def generate(
        db: Session,
        session_id: uuid.UUID,
        *,
        use_llm_narrative: bool = True,
    ) -> Case:
        """Generate (or regenerate) the case summary for a session."""
        session = db.get(IntakeSession, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Intake session with ID {session_id} not found",
            )
        if session.status in (SessionStatus.CREATED.value, SessionStatus.CANCELLED.value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot generate a case summary for a session with status "
                    f"'{session.status}'."
                ),
            )

        case = db.scalars(select(Case).where(Case.session_id == session.id)).first()

        summary = CaseSummaryService.build_summary(db, session)

        # Corrections: patient first, then doctor (doctor always wins and is
        # re-applied on every regeneration).
        if case is not None:
            summary = CaseSummaryService._apply_corrections(db, case, summary)

        chief = _get_path(summary, "current_consultation.chief_complaint.value")
        narrative, narrative_source, model_name = CaseSummaryService._build_narrative(
            summary, use_llm_narrative=use_llm_narrative
        )
        summary["narrative_source"] = narrative_source
        summary["generated_by_model"] = model_name

        now = utcnow()
        if case is None:
            case = Case(
                id=uuid.uuid4(),
                session_id=session.id,
                patient_id=session.patient_id,
                hospital_id=session.hospital_id,
                medical_stream_id=session.medical_stream_id,
                department_id=session.department_id,
                status=CaseStatus.DRAFT.value,
            )
            db.add(case)

        case.chief_complaint = chief
        case.summary = summary
        case.summary_text = narrative
        case.generated_by_model = model_name
        case.generated_at = now
        if session.status == SessionStatus.PATIENT_CONFIRMED.value:
            case.status = CaseStatus.PATIENT_CONFIRMED.value
        if any(
            e.editor_type == EditorType.DOCTOR.value for e in (case.edits or [])
        ):
            case.status = CaseStatus.DOCTOR_VERIFIED.value

        # Advance the session only along a legal transition. Phase 8 owns
        # patient review/confirmation, so a summary generated before that leaves
        # the session status untouched.
        if session.status == SessionStatus.PATIENT_CONFIRMED.value:
            session.status = SessionStatus.SUMMARY_GENERATED.value

        db.commit()
        db.refresh(case)

        log.info(
            "Case summary generated",
            extra={
                "session_id": str(session.id),
                "case_id": str(case.id),
                "narrative_source": narrative_source,
                "history_available": bool(_get_path(summary, "previous_history.available")),
                "llm_success": narrative_source == "llm",
            },
        )
        return case

    @staticmethod
    def get_case(db: Session, case_id: uuid.UUID) -> Case:
        case = db.get(Case, case_id)
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case with ID {case_id} not found",
            )
        return case

    @staticmethod
    def get_case_for_session(db: Session, session_id: uuid.UUID) -> Optional[Case]:
        return db.scalars(select(Case).where(Case.session_id == session_id)).first()

    # ── Deterministic assembly ────────────────────────────────────────────

    @staticmethod
    def build_summary(db: Session, session: IntakeSession) -> dict[str, Any]:
        """Assemble the structured summary. No LLM involvement whatsoever."""
        workflow = None
        if session.medical_stream_id:
            try:
                workflow = WorkflowService.get_active_workflow(
                    db,
                    medical_stream_id=session.medical_stream_id,
                    department_id=session.department_id,
                )
            except HTTPException:
                workflow = None

        stream_code = session.medical_stream.code if session.medical_stream else None
        is_ayush = stream_code == AYUSH_STREAM_CODE

        current, ayush_findings = CaseSummaryService._build_current_consultation(
            db, session, workflow, is_ayush=is_ayush
        )

        historical = HistoricalContextService.build(
            db, patient_id=session.patient_id, current_session_id=session.id
        )

        summary: dict[str, Any] = {
            "schema_version": SUMMARY_SCHEMA_VERSION,
            "generated_at": utcnow().isoformat(),
            "generated_by_model": None,
            "narrative_source": None,
            "workflow": {
                "medical_stream_code": stream_code,
                "department_code": session.department.code if session.department else None,
                "workflow_code": workflow.code if workflow else None,
                "workflow_name": workflow.name if workflow else None,
                "summary_template": AYUSH_STREAM_CODE if is_ayush else "MODERN_MEDICINE",
            },
            "current_consultation": current,
            "previous_history": historical.as_summary_block(),
            "ayush_assessment": (
                {"findings": ayush_findings} if is_ayush else None
            ),
            "patient_corrections": [],
            "doctor_verified_fields": [],
            "data_availability": {
                "interview": bool(current.get("interview_responses")),
                "vitals": current.get("vitals") is not None,
                "alerts": bool(current.get("alerts")),
                "documents": historical.document_count > 0,
                "document_extractions": historical.extraction_count > 0,
                "timeline": historical.timeline_event_count > 0,
                "previous_sessions": historical.previous_session_count > 0,
                "previous_history": historical.available,
            },
            "safety": {
                "assembled_deterministically": True,
                "contains_diagnosis": False,
                "contains_prescription": False,
                "asserts_causality": False,
                "note": (
                    "Information collection only. Current and previous "
                    "information are reported separately and no relationship "
                    "between them is asserted."
                ),
            },
        }
        return summary

    @staticmethod
    def _build_current_consultation(
        db: Session,
        session: IntakeSession,
        workflow: Any,
        *,
        is_ayush: bool,
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Assemble the current session block from THIS session's answers only."""
        policy = policy_for_workflow(workflow)

        # Strictly scoped to the session under summary. This is what guarantees a
        # previous session's answers can never be read as today's interview.
        answers = list(
            db.scalars(
                select(Answer)
                .where(Answer.session_id == session.id)
                .order_by(Answer.answered_at.asc())
            ).all()
        )
        question_ids = {a.question_id for a in answers if a.question_id}
        questions: dict[uuid.UUID, Question] = {}
        if question_ids:
            questions = {
                q.id: q
                for q in db.scalars(select(Question).where(Question.id.in_(question_ids))).all()
            }

        hpi: dict[str, Any] = {
            "primary_complaint": None,
            "duration": None,
            "onset": None,
            "severity": None,
            "progression": None,
            "associated_symptoms": [],
        }
        chief_complaint: Optional[dict[str, Any]] = None
        review_of_systems: list[dict[str, Any]] = []
        ayush_findings: list[dict[str, Any]] = []
        responses: list[dict[str, Any]] = []
        seen_associated: set[str] = set()

        for answer in answers:
            question = questions.get(answer.question_id) if answer.question_id else None
            envelope = answer.normalized_answer if isinstance(answer.normalized_answer, dict) else {}
            clinical = envelope.get(CLINICAL_KEY) if isinstance(envelope, dict) else None
            facts = envelope.get(FACTS_KEY) if isinstance(envelope, dict) else None
            categories = envelope.get(CATEGORIES_KEY) if isinstance(envelope, dict) else None
            source = (
                InformationSource.PATIENT_CORRECTION.value
                if answer.is_patient_corrected
                else InformationSource.PATIENT_INTERVIEW.value
            )
            source_ref = {
                "type": "answer",
                "answer_id": str(answer.id),
                "session_id": str(session.id),
                "question_id": str(answer.question_id) if answer.question_id else None,
                "question_code": question.question_code if question else None,
            }
            confidence = float(answer.confidence) if answer.confidence is not None else None
            recorded_at = answer.answered_at.isoformat() if answer.answered_at else None

            responses.append(
                {
                    "question_code": question.question_code if question else None,
                    "question": question.question_text if question else None,
                    "category": question.category if question else None,
                    "answer": _clean(answer.raw_answer),
                    "answer_type": answer.answer_type,
                    "source": source,
                    "source_ref": source_ref,
                    "confidence": confidence,
                    "is_patient_corrected": bool(answer.is_patient_corrected),
                    "recorded_at": recorded_at,
                }
            )

            def make(value: str, detail: Optional[dict[str, Any]] = None) -> dict[str, Any]:
                return history_item(
                    value,
                    source,
                    source_ref=source_ref,
                    confidence=confidence,
                    recorded_at=recorded_at,
                    detail=detail,
                )

            # ── Reuse the Phase 5B structured clinical block ──────────────
            if isinstance(clinical, dict):
                primary = clinical.get("primary_complaint")
                if isinstance(primary, dict):
                    symptom = _clean(primary.get("symptom"))
                    if symptom and hpi["primary_complaint"] is None:
                        hpi["primary_complaint"] = make(symptom, detail=primary)
                        chief_complaint = make(symptom, detail=primary)
                    for key in ("duration", "onset", "severity"):
                        value = _clean(primary.get(key))
                        if value and hpi[key] is None:
                            hpi[key] = make(value)
                for entry in clinical.get("associated_symptoms") or []:
                    if not isinstance(entry, dict):
                        continue
                    symptom = _clean(entry.get("symptom"))
                    if not symptom or symptom.lower() in seen_associated:
                        continue
                    seen_associated.add(symptom.lower())
                    hpi["associated_symptoms"].append(make(symptom, detail=entry))
                progression = _clean(clinical.get("progression"))
                if progression and hpi["progression"] is None:
                    hpi["progression"] = make(progression)

            # Fall back to the flat fact map when no clinical block exists.
            if isinstance(facts, dict):
                if hpi["primary_complaint"] is None:
                    symptom = _clean(facts.get("symptom"))
                    if symptom:
                        hpi["primary_complaint"] = make(symptom)
                        chief_complaint = make(symptom)
                for key in ("duration", "onset", "severity", "progression"):
                    if hpi[key] is None:
                        value = _clean(facts.get(key))
                        if value:
                            hpi[key] = make(value)

            # ── Category-driven placement ─────────────────────────────────
            canonical = policy.canonical(question.category) if question else None
            raw = _clean(answer.raw_answer)
            if canonical and raw:
                if is_ayush and canonical in _AYUSH_CATEGORIES:
                    ayush_findings.append(
                        {
                            "category": question.category,
                            "value": raw,
                            "source": source,
                            "source_ref": source_ref,
                            "confidence": confidence,
                        }
                    )
                elif canonical not in _HPI_CATEGORIES:
                    entry = make(raw)
                    entry["category"] = question.category
                    review_of_systems.append(entry)

            # Chief complaint fallback: the answer to the chief-complaint question.
            if chief_complaint is None and canonical == "CHIEF_COMPLAINT" and raw:
                chief_complaint = make(raw)
                if hpi["primary_complaint"] is None:
                    hpi["primary_complaint"] = make(raw)

            if isinstance(categories, list) and not canonical and raw and chief_complaint is None:
                if "CHIEF_COMPLAINT" in categories:
                    chief_complaint = make(raw)

        vitals_block = CaseSummaryService._build_vitals(db, session)
        alerts_block = CaseSummaryService._build_alerts(db, session)

        current = {
            "session_id": str(session.id),
            "session_date": (
                session.started_at.isoformat()
                if session.started_at
                else session.created_at.isoformat()
            ),
            "session_status": session.status,
            "chief_complaint": chief_complaint,
            "history_of_present_illness": hpi,
            "review_of_systems": review_of_systems,
            "interview_responses": responses,
            "vitals": vitals_block,
            "alerts": alerts_block,
        }
        return current, ayush_findings

    @staticmethod
    def _build_vitals(db: Session, session: IntakeSession) -> Optional[dict[str, Any]]:
        vital = db.scalars(
            select(Vital)
            .where(Vital.session_id == session.id)
            .order_by(Vital.measured_at.desc())
        ).first()
        if vital is None:
            return None
        measurements = {}
        for field_name in _VITAL_FIELDS:
            value = getattr(vital, field_name, None)
            if value is not None:
                measurements[field_name] = float(value) if not isinstance(value, int) else value
        if not measurements:
            return None
        return {
            "measurements": measurements,
            "source": InformationSource.VITAL_MEASUREMENT.value,
            "source_ref": {"type": "vital", "vital_id": str(vital.id)},
            "measured_at": vital.measured_at.isoformat() if vital.measured_at else None,
            "device_source": vital.source,
        }

    @staticmethod
    def _build_alerts(db: Session, session: IntakeSession) -> list[dict[str, Any]]:
        alerts = list(
            db.scalars(
                select(Alert)
                .where(
                    Alert.session_id == session.id,
                    Alert.status == AlertStatus.ACTIVE.value,
                )
                .order_by(Alert.created_at.asc())
            ).all()
        )
        return [
            {
                "alert_id": str(a.id),
                "alert_type": a.alert_type,
                "severity": a.severity,
                "title": _clean(a.title),
                "message": _clean(a.message),
                "status": a.status,
                "trigger_value": a.trigger_value,
                "source_ref": {"type": "alert", "alert_id": str(a.id)},
            }
            for a in alerts
        ]

    # ── Corrections ───────────────────────────────────────────────────────

    @staticmethod
    def _apply_corrections(
        db: Session, case: Case, summary: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply patient then doctor corrections over the freshly built draft.

        Patient corrections override the AI draft (§28). Doctor corrections are
        applied last and re-applied on every regeneration, so AI output can never
        silently overwrite doctor-verified information (§33).
        """
        edits = list(
            db.scalars(
                select(CaseEdit)
                .where(CaseEdit.case_id == case.id)
                .order_by(CaseEdit.created_at.asc())
            ).all()
        )
        applied_patient: list[dict[str, Any]] = []
        doctor_fields: list[str] = []

        for editor_type in (EditorType.PATIENT.value, EditorType.DOCTOR.value):
            for edit in edits:
                if edit.editor_type != editor_type:
                    continue
                new_value = edit.new_value
                # new_value is JSONB; unwrap the conventional {"value": ...} form.
                payload = (
                    new_value.get("value")
                    if isinstance(new_value, dict) and "value" in new_value
                    else new_value
                )
                target = _get_path(summary, edit.field_name)
                if isinstance(target, dict) and "value" in target:
                    replacement = dict(target)
                    replacement["value"] = payload
                    replacement["source"] = (
                        InformationSource.PATIENT_CORRECTION.value
                        if editor_type == EditorType.PATIENT.value
                        else InformationSource.DOCTOR_VERIFICATION.value
                    )
                    replacement["source_ref"] = {
                        "type": "case_edit",
                        "case_edit_id": str(edit.id),
                        "editor_type": editor_type,
                    }
                    ok = _set_path(summary, edit.field_name, replacement)
                else:
                    ok = _set_path(summary, edit.field_name, payload)

                if not ok:
                    log.info(
                        "Skipped correction for unknown summary path",
                        extra={"case_id": str(case.id), "field_name": edit.field_name},
                    )
                    continue

                if editor_type == EditorType.PATIENT.value:
                    applied_patient.append(
                        {
                            "field_name": edit.field_name,
                            "old_value": edit.old_value,
                            "new_value": payload,
                            "reason": edit.reason,
                            "corrected_at": edit.created_at.isoformat(),
                            "source": InformationSource.PATIENT_CORRECTION.value,
                        }
                    )
                else:
                    doctor_fields.append(edit.field_name)

        summary["patient_corrections"] = applied_patient
        summary["doctor_verified_fields"] = sorted(set(doctor_fields))
        return summary

    # ── Narrative ─────────────────────────────────────────────────────────

    @staticmethod
    def _build_narrative(
        summary: dict[str, Any], *, use_llm_narrative: bool
    ) -> tuple[str, str, Optional[str]]:
        """Return (narrative, source, model_name).

        The deterministic narrative is always computed first and is used whenever
        the LLM is unavailable or its output fails validation.
        """
        deterministic = build_deterministic_narrative(summary)
        if not use_llm_narrative or not settings.llm_enabled:
            return deterministic, "deterministic", None

        try:
            from app.services.llm import get_llm_service

            service = get_llm_service()
            raw = service.summarise_case(summary)
            validated = validate_narrative(raw)
            return validated, "llm", settings.OPENAI_MODEL
        except NarrativeRejected as exc:
            log.warning(
                "LLM narrative rejected by safety validation — using deterministic text",
                extra={"rejection": exc.reason, "llm_success": False, "fallback_used": True},
            )
            return deterministic, "deterministic", None
        except Exception as exc:
            log.info(
                "LLM narrative unavailable — using deterministic text",
                extra={
                    "error_class": type(exc).__name__,
                    "llm_success": False,
                    "fallback_used": True,
                },
            )
            return deterministic, "deterministic", None
