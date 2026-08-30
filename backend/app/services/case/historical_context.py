"""Historical patient context retrieval for the case summary (Phase 5C).

HARD RULE
    Everything returned by this module is HISTORICAL — it belongs under
    ``previous_history`` in the case summary and must never be merged into the
    current consultation. The current session's own answers are assembled
    separately by CaseSummaryService and are never read here.

    The one exception is deliberate and explicit: previous *sessions* contribute
    their chief complaint to ``previous_consultations`` so a doctor can see what
    the patient came in for before. Those are labelled with their own session id
    and date, and never populate any current-consultation field.

NEVER FABRICATE
    Every item comes from a real row. When a patient has no documents, timeline
    events or prior sessions, the corresponding lists come back empty and
    ``available`` is False. Nothing is inferred, and no causal link is drawn
    between any historical entry and the current complaint.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentExtraction, ExtractionStatus
from app.models.intake_session import IntakeSession, SessionStatus
from app.models.timeline_event import InformationSource, TimelineEvent, TimelineEventType
from app.services.llm.schemas import CATEGORIES_KEY, CLINICAL_KEY, FACTS_KEY

# Timeline event types that feed each historical section.
_TIMELINE_SECTION_MAP: dict[str, str] = {
    TimelineEventType.DIAGNOSIS.value: "past_medical_history",
    TimelineEventType.PRESCRIPTION.value: "drug_history",
    TimelineEventType.LAB_REPORT.value: "previous_investigations",
    TimelineEventType.PROCEDURE.value: "past_surgical_history",
    TimelineEventType.HOSPITAL_ADMISSION.value: "past_surgical_history",
    TimelineEventType.ALLERGY.value: "allergy_history",
    TimelineEventType.FAMILY_HISTORY.value: "family_history",
    TimelineEventType.PERSONAL_HISTORY.value: "personal_history",
}

# DocumentExtraction JSONB column -> historical section.
_EXTRACTION_SECTION_MAP: list[tuple[str, str]] = [
    ("diagnoses", "past_medical_history"),
    ("medications", "drug_history"),
    ("investigations", "previous_investigations"),
    ("procedures", "past_surgical_history"),
    ("allergies", "allergy_history"),
]

HISTORY_SECTIONS = (
    "past_medical_history",
    "past_surgical_history",
    "drug_history",
    "allergy_history",
    "family_history",
    "personal_history",
    "previous_investigations",
)


def _clean(value: Any) -> Optional[str]:
    """Normalize a value to a non-empty display string, or None."""
    if value is None:
        return None
    text = " ".join(str(value).split())
    return text or None


def _entry_label(entry: Any) -> Optional[str]:
    """Derive a display label from one extraction entry.

    Extraction entries are objects like ``{"name": "Metformin", "dose": "500 mg"}``
    or plain strings. Only fields actually present are used.
    """
    if isinstance(entry, str):
        return _clean(entry)
    if not isinstance(entry, dict):
        return _clean(entry)

    name = _clean(entry.get("name") or entry.get("title") or entry.get("value"))
    if not name:
        return None
    parts = [name]
    dose = _clean(entry.get("dose") or entry.get("dosage"))
    if dose:
        parts.append(dose)
    result = _clean(entry.get("result"))
    value = _clean(entry.get("value"))
    if value and value != name:
        parts.append(value)
    elif result:
        parts.append(result)
    return " ".join(parts)


def _entry_confidence(entry: Any, fallback: Optional[float]) -> Optional[float]:
    if isinstance(entry, dict) and entry.get("confidence") is not None:
        try:
            return max(0.0, min(1.0, float(entry["confidence"])))
        except (TypeError, ValueError):
            return fallback
    return fallback


def history_item(
    value: str,
    source: str,
    *,
    source_ref: Optional[dict[str, Any]] = None,
    confidence: Optional[float] = None,
    recorded_at: Optional[str] = None,
    detail: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build one traceable summary item.

    ``source`` is always a value of InformationSource so a doctor can tell where
    the statement came from (§23), and ``source_ref`` points at the originating
    row.
    """
    return {
        "value": value,
        "source": source,
        "source_ref": source_ref,
        "confidence": confidence,
        "recorded_at": recorded_at,
        "detail": detail or None,
    }


@dataclass
class HistoricalContext:
    """Everything historical known about a patient, already sectioned."""

    sections: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    timeline: list[dict[str, Any]] = field(default_factory=list)
    previous_consultations: list[dict[str, Any]] = field(default_factory=list)
    document_count: int = 0
    extraction_count: int = 0
    timeline_event_count: int = 0
    previous_session_count: int = 0

    @property
    def available(self) -> bool:
        """True when any real historical record exists for this patient."""
        return bool(
            self.timeline
            or self.previous_consultations
            or any(self.sections.get(s) for s in HISTORY_SECTIONS)
        )

    def as_summary_block(self) -> dict[str, Any]:
        block: dict[str, Any] = {"available": self.available}
        for section in HISTORY_SECTIONS:
            block[section] = self.sections.get(section, [])
        block["timeline"] = self.timeline
        block["previous_consultations"] = self.previous_consultations
        block["sources_scanned"] = {
            "documents": self.document_count,
            "document_extractions": self.extraction_count,
            "timeline_events": self.timeline_event_count,
            "previous_sessions": self.previous_session_count,
        }
        return block


class HistoricalContextService:
    """Reads a patient's real historical records from PostgreSQL."""

    @staticmethod
    def build(
        db: Session,
        patient_id: uuid.UUID,
        current_session_id: uuid.UUID,
    ) -> HistoricalContext:
        """Collect historical context for one patient.

        ``current_session_id`` is EXCLUDED from every query, so the session being
        summarised can never contribute to its own history.
        """
        ctx = HistoricalContext(sections={s: [] for s in HISTORY_SECTIONS})
        seen: dict[str, set[str]] = {s: set() for s in HISTORY_SECTIONS}

        def add(section: str, item: dict[str, Any]) -> None:
            key = item["value"].strip().lower()
            if not key or key in seen[section]:
                return
            seen[section].add(key)
            ctx.sections[section].append(item)

        # ── 1. Document extractions (source: DOCUMENT_OCR) ─────────────────
        doc_rows = list(
            db.execute(
                select(Document, DocumentExtraction)
                .join(DocumentExtraction, DocumentExtraction.document_id == Document.id)
                .where(
                    Document.patient_id == patient_id,
                    Document.deleted_at.is_(None),
                    DocumentExtraction.status.in_(
                        [
                            ExtractionStatus.COMPLETED.value,
                            ExtractionStatus.REVIEW_REQUIRED.value,
                        ]
                    ),
                )
                .order_by(Document.uploaded_at.desc())
            ).all()
        )
        ctx.document_count = len(doc_rows)
        ctx.extraction_count = len(doc_rows)

        for document, extraction in doc_rows:
            source_ref = {
                "type": "document",
                "document_id": str(document.id),
                "document_type": document.document_type,
                "original_filename": document.original_filename,
                "document_date": (
                    document.document_date.isoformat() if document.document_date else None
                ),
            }
            recorded_at = (
                document.document_date.isoformat()
                if document.document_date
                else (document.uploaded_at.isoformat() if document.uploaded_at else None)
            )
            overall = (
                float(extraction.overall_confidence)
                if extraction.overall_confidence is not None
                else None
            )
            for column, section in _EXTRACTION_SECTION_MAP:
                entries = getattr(extraction, column, None)
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    label = _entry_label(entry)
                    if not label:
                        continue
                    add(
                        section,
                        history_item(
                            label,
                            InformationSource.DOCUMENT_OCR.value,
                            source_ref=source_ref,
                            confidence=_entry_confidence(entry, overall),
                            recorded_at=recorded_at,
                            detail=entry if isinstance(entry, dict) else None,
                        ),
                    )

        # ── 2. Timeline events ────────────────────────────────────────────
        events = list(
            db.scalars(
                select(TimelineEvent)
                .where(TimelineEvent.patient_id == patient_id)
                .order_by(TimelineEvent.event_date.desc())
            ).all()
        )
        # A timeline event generated from the session under summary is not
        # history for that same session.
        events = [e for e in events if e.session_id != current_session_id]
        ctx.timeline_event_count = len(events)

        for event in events:
            source_ref: dict[str, Any] = {"type": "timeline_event", "timeline_event_id": str(event.id)}
            if event.document_id:
                source_ref["document_id"] = str(event.document_id)
            if event.session_id:
                source_ref["session_id"] = str(event.session_id)
            recorded_at = event.event_date.isoformat() if event.event_date else None
            confidence = float(event.confidence) if event.confidence is not None else None

            ctx.timeline.append(
                {
                    "event_date": recorded_at,
                    "event_type": event.event_type,
                    "title": _clean(event.title) or "",
                    "description": _clean(event.description),
                    "source": event.source_type,
                    "source_ref": source_ref,
                    "confidence": confidence,
                }
            )

            section = _TIMELINE_SECTION_MAP.get(event.event_type)
            if not section:
                continue
            label = _clean(event.title)
            if not label:
                continue
            add(
                section,
                history_item(
                    label,
                    event.source_type or InformationSource.DOCUMENT_OCR.value,
                    source_ref=source_ref,
                    confidence=confidence,
                    recorded_at=recorded_at,
                    detail={"description": _clean(event.description)}
                    if event.description
                    else None,
                ),
            )

        # ── 3. Previous consultations (chief complaint only) ───────────────
        previous_sessions = list(
            db.scalars(
                select(IntakeSession)
                .where(
                    IntakeSession.patient_id == patient_id,
                    IntakeSession.id != current_session_id,
                    IntakeSession.status.notin_(
                        [SessionStatus.CANCELLED.value, SessionStatus.CREATED.value]
                    ),
                )
                .order_by(IntakeSession.created_at.desc())
            ).all()
        )
        ctx.previous_session_count = len(previous_sessions)

        for prior in previous_sessions:
            complaint = HistoricalContextService._session_chief_complaint(db, prior.id)
            if complaint is None:
                continue
            ctx.previous_consultations.append(
                {
                    "session_id": str(prior.id),
                    "session_date": (
                        prior.started_at.isoformat()
                        if prior.started_at
                        else prior.created_at.isoformat()
                    ),
                    "status": prior.status,
                    "department_code": prior.department.code if prior.department else None,
                    "medical_stream_code": (
                        prior.medical_stream.code if prior.medical_stream else None
                    ),
                    "chief_complaint": complaint,
                    "source": InformationSource.PATIENT_INTERVIEW.value,
                    "source_ref": {"type": "intake_session", "session_id": str(prior.id)},
                }
            )

        return ctx

    @staticmethod
    def _session_chief_complaint(db: Session, session_id: uuid.UUID) -> Optional[str]:
        """Chief complaint recorded in one prior session, from its stored facts.

        Reuses the Phase 5B structured facts rather than re-extracting from
        raw_answer. Returns None when that session captured no complaint.
        """
        from app.models.answer import Answer

        answers = list(
            db.scalars(
                select(Answer)
                .where(Answer.session_id == session_id)
                .order_by(Answer.answered_at.asc())
            ).all()
        )
        for answer in answers:
            envelope = answer.normalized_answer or {}
            if not isinstance(envelope, dict):
                continue
            clinical = envelope.get(CLINICAL_KEY)
            if isinstance(clinical, dict):
                primary = clinical.get("primary_complaint")
                if isinstance(primary, dict):
                    symptom = _clean(primary.get("symptom"))
                    if symptom:
                        return symptom
            facts = envelope.get(FACTS_KEY)
            if isinstance(facts, dict):
                symptom = _clean(facts.get("symptom"))
                if symptom:
                    return symptom
            categories = envelope.get(CATEGORIES_KEY)
            if isinstance(categories, list) and "CHIEF_COMPLAINT" in categories:
                raw = _clean(answer.raw_answer)
                if raw:
                    return raw
        return None
