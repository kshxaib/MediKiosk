"""Case summary narrative generation and safety validation (Phase 5C).

The structured ``Case.summary`` JSONB is assembled deterministically and is the
authoritative artifact. This module produces only the optional human-readable
``summary_text`` rendering of it.

SAFETY MODEL
    A deterministic narrative is ALWAYS available. When an LLM narrative is
    generated it must pass every validator below or it is discarded and the
    deterministic text is used instead. The LLM never sees raw patient answers —
    only the already-assembled structured summary — so it has nothing to invent
    history from.

    Validators reject:
      - causal language linking history to the current complaint
      - diagnostic assertions
      - prescription / treatment recommendations
      - narratives longer than the cap

    Note: the interview-question keyword blocklist is deliberately NOT reused
    here. A case summary must be able to say "Diabetes" and "Metformin" when
    those come from a real previous record; blocking the words would make
    genuine history unreportable. What is blocked is the model ASSERTING a
    diagnosis, prescribing, or inventing causality.
"""
from __future__ import annotations

import re
from typing import Any, Optional

MAX_NARRATIVE_CHARS = 3000

# Phrases that would assert causality between history and the current complaint.
_CAUSAL_PATTERNS = (
    "caused by", "causing", "because of", "due to", "secondary to",
    "as a result of", "results from", "resulting from", "leading to", "led to",
    "attributable to", "explains the", "explained by", "responsible for",
    "brought on by", "triggered by", "stems from", "arising from",
    "related to the", "linked to", "associated with the diagnosis",
    "complication of", "manifestation of",
)

# Phrases that would assert a diagnosis.
_DIAGNOSTIC_PATTERNS = (
    "diagnosis is", "diagnosed as", "the diagnosis", "likely has", "probably has",
    "appears to have", "suggests a", "suggestive of", "consistent with",
    "indicative of", "points to", "differential diagnosis", "rule out",
    "most likely", "impression:", "we believe the patient has",
    "the patient has ", "patient is suffering from",
)

# Phrases that would recommend treatment.
_TREATMENT_PATTERNS = (
    "should take", "should be given", "should start", "recommend starting",
    "recommend taking", "advise taking", "prescribe", "prescribed for this",
    "treatment plan", "we recommend", "is recommended", "management plan",
    "should be treated", "consider starting", "initiate therapy", "dose should",
)

_WS_RE = re.compile(r"\s+")

# Internal identifiers must never surface in doctor-facing prose. Prompt guidance
# alone is not a guarantee, so this is enforced deterministically.
_UUID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.IGNORECASE
)
_INTERNAL_FIELD_RE = re.compile(
    r"\b(source_ref|recorded_at|schema_version|[a-z_]*_id)\b", re.IGNORECASE
)


class NarrativeRejected(Exception):
    """Raised when an LLM narrative fails deterministic safety validation."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def validate_narrative(text: str) -> str:
    """Return the cleaned narrative, or raise NarrativeRejected.

    Deterministic: no model involvement. This is the safety boundary.
    """
    cleaned = _WS_RE.sub(" ", (text or "")).strip()
    if not cleaned:
        raise NarrativeRejected("empty_narrative")
    if len(cleaned) > MAX_NARRATIVE_CHARS:
        raise NarrativeRejected("too_long")

    lowered = cleaned.lower()
    for phrase in _CAUSAL_PATTERNS:
        if phrase in lowered:
            raise NarrativeRejected(f"causal_language:{phrase}")
    for phrase in _DIAGNOSTIC_PATTERNS:
        if phrase in lowered:
            raise NarrativeRejected(f"diagnostic_assertion:{phrase}")
    for phrase in _TREATMENT_PATTERNS:
        if phrase in lowered:
            raise NarrativeRejected(f"treatment_recommendation:{phrase}")
    if _UUID_RE.search(cleaned):
        raise NarrativeRejected("leaked_internal_identifier")
    if _INTERNAL_FIELD_RE.search(cleaned):
        raise NarrativeRejected("leaked_internal_field_name")
    return cleaned


# ─── Deterministic narrative ──────────────────────────────────────────────────

def _items_text(items: list[dict[str, Any]], limit: int = 12) -> Optional[str]:
    values = [str(i.get("value")).strip() for i in items[:limit] if i.get("value")]
    return "; ".join(values) if values else None


def _hpi_text(hpi: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    order = [
        ("primary_complaint", "Primary complaint"),
        ("duration", "Duration"),
        ("onset", "Onset"),
        ("severity", "Severity"),
        ("progression", "Progression"),
    ]
    for key, label in order:
        item = hpi.get(key)
        if isinstance(item, dict) and item.get("value"):
            lines.append(f"  {label}: {item['value']}")
    associated = hpi.get("associated_symptoms")
    if isinstance(associated, list) and associated:
        rendered = []
        for entry in associated:
            if not isinstance(entry, dict):
                continue
            value = entry.get("value")
            if not value:
                continue
            detail = entry.get("detail") or {}
            timing = detail.get("onset") or detail.get("duration")
            rendered.append(f"{value} ({timing})" if timing else str(value))
        if rendered:
            lines.append(f"  Associated symptoms: {'; '.join(rendered)}")
    return lines


def build_deterministic_narrative(summary: dict[str, Any]) -> str:
    """Render the structured summary as plain text, with zero interpretation.

    Current and historical information are printed under separate headings and
    never combined into one statement.
    """
    current = summary.get("current_consultation") or {}
    history = summary.get("previous_history") or {}
    lines: list[str] = ["CURRENT CONSULTATION"]

    chief = current.get("chief_complaint")
    if isinstance(chief, dict) and chief.get("value"):
        lines.append(f"  Chief complaint: {chief['value']}")
    else:
        lines.append("  Chief complaint: not recorded")

    hpi_lines = _hpi_text(current.get("history_of_present_illness") or {})
    if hpi_lines:
        lines.append("  History of present illness:")
        lines.extend(f"  {line}" for line in hpi_lines)

    ros = current.get("review_of_systems")
    if isinstance(ros, list) and ros:
        rendered = _items_text(ros)
        if rendered:
            lines.append(f"  Review of systems: {rendered}")

    vitals = current.get("vitals")
    if isinstance(vitals, dict) and vitals.get("measurements"):
        readings = "; ".join(
            f"{k.replace('_', ' ')}: {v}" for k, v in vitals["measurements"].items() if v is not None
        )
        if readings:
            lines.append(f"  Vitals: {readings}")
    else:
        lines.append("  Vitals: not recorded")

    alerts = current.get("alerts")
    if isinstance(alerts, list) and alerts:
        for alert in alerts:
            lines.append(
                f"  Alert ({alert.get('severity')}): {alert.get('title')} — "
                f"{alert.get('message')}"
            )

    lines.append("")
    if history.get("available"):
        lines.append("PREVIOUS HISTORY (from earlier records — not part of today's complaint)")
        section_labels = [
            ("past_medical_history", "Past medical history"),
            ("past_surgical_history", "Past surgical history"),
            ("drug_history", "Drug history"),
            ("allergy_history", "Allergy history"),
            ("family_history", "Family history"),
            ("personal_history", "Personal history"),
            ("previous_investigations", "Previous investigations"),
        ]
        for key, label in section_labels:
            rendered = _items_text(history.get(key) or [])
            lines.append(f"  {label}: {rendered}" if rendered else f"  {label}: not available")
        prior = history.get("previous_consultations")
        if isinstance(prior, list) and prior:
            rendered = "; ".join(
                f"{p.get('session_date', '')[:10]}: {p.get('chief_complaint')}"
                for p in prior
                if p.get("chief_complaint")
            )
            if rendered:
                lines.append(f"  Previous consultations: {rendered}")
    else:
        lines.append("PREVIOUS HISTORY")
        lines.append("  No previous records available for this patient.")

    ayush = summary.get("ayush_assessment")
    if isinstance(ayush, dict) and ayush.get("findings"):
        lines.append("")
        lines.append("AYURVEDIC ASSESSMENT")
        for finding in ayush["findings"]:
            if isinstance(finding, dict) and finding.get("value"):
                lines.append(f"  {finding.get('category')}: {finding['value']}")

    corrections = summary.get("patient_corrections")
    if isinstance(corrections, list) and corrections:
        lines.append("")
        lines.append("PATIENT CORRECTIONS")
        for correction in corrections:
            lines.append(
                f"  {correction.get('field_name')}: "
                f"{correction.get('new_value')} (corrected by patient)"
            )

    lines.append("")
    lines.append(
        "This summary organises collected information for clinical review. "
        "It contains no diagnosis, no treatment recommendation, and asserts no "
        "relationship between previous records and today's complaint."
    )
    return "\n".join(lines)
