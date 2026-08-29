"""Structured Pydantic schemas for LLM input/output (Phase 5B).

These are INTERNAL schemas — never returned directly to the patient UI.

SCHEMA DESIGN NOTE (OpenAI structured output):
    OpenAI's strict Structured Outputs mode does not support open-ended objects
    (``dict[str, Any]`` converts to ``{"type": "object", "additionalProperties":
    false}`` with no declared properties, which can only ever match ``{}``).
    Every LLM-facing model here therefore uses explicit, closed shapes — facts
    are returned as a ``list[ExtractedFact]`` of key/value pairs and folded into
    a dict by the backend, not requested as a free-form mapping.
"""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

# ─── Persisted normalized_answer envelope ────────────────────────────────────
# Answer.normalized_answer is JSONB, so the structured extraction is stored
# in-place under stable reserved keys instead of requiring a new migration.
FACTS_KEY = "facts"
CATEGORIES_KEY = "categories_satisfied"
RAW_FALLBACK_KEY = "raw_fallback"
AD_HOC_KEY = "ad_hoc_question"
CLINICAL_KEY = "clinical"
ENVELOPE_KEYS = frozenset({
    FACTS_KEY, CATEGORIES_KEY, RAW_FALLBACK_KEY, AD_HOC_KEY, CLINICAL_KEY,
})


# ─── LLM INPUT ───────────────────────────────────────────────────────────────

class PreviousAnswerSummary(BaseModel):
    """Compact representation of one answered question.

    ``raw_answer`` is untrusted patient text and is always rendered inside a
    clearly delimited data block by the prompt builder.
    """
    category: Optional[str] = None
    question_code: Optional[str] = None
    question_text: str
    answer_type: str
    raw_answer: Optional[str] = None  # included only for TEXT/NUMBER/VOICE types
    facts: dict[str, Any] = Field(default_factory=dict)
    categories_satisfied: list[str] = Field(default_factory=list)
    # Secondary symptoms with their own timing, so the question engine can see
    # them instead of having them silently flattened away.
    associated_symptoms: list[dict[str, Any]] = Field(default_factory=list)


class ClinicalContext(BaseModel):
    """Compact clinical context passed to the LLM.

    Token budget is kept minimal — we never send the full session history
    or any sensitive fields (face embeddings, patient IDs, etc.).
    """
    session_id: str
    language: str = "en"
    medical_stream_code: str
    department_code: str
    workflow_code: str
    workflow_name: str
    # Categories whose question already has an Answer row (question_id join).
    answered_categories: list[str] = Field(default_factory=list)
    # Union of answered_categories and every category satisfied by extracted
    # facts. This is what the LLM must treat as "already collected".
    satisfied_categories: list[str] = Field(default_factory=list)
    # Genuinely missing: workflow categories minus satisfied_categories.
    remaining_categories: list[str] = Field(default_factory=list)
    # Merged structured facts collected so far this session.
    known_facts: dict[str, Any] = Field(default_factory=dict)
    # Last 10 answers at most — keeps context bounded
    recent_answers: list[PreviousAnswerSummary] = Field(default_factory=list)
    total_questions: int = 0
    completed_questions: int = 0
    # Available question codes the LLM may select from (unanswered AND not
    # already satisfied by known facts).
    available_question_codes: list[str] = Field(default_factory=list)
    # Free-text questions already asked ad hoc this session, so the LLM does
    # not propose them again.
    previously_generated_questions: list[str] = Field(default_factory=list)


# ─── LLM OUTPUT ──────────────────────────────────────────────────────────────

ALLOWED_QUESTION_TYPES = frozenset({"TEXT", "NUMBER", "YES_NO", "SINGLE_CHOICE"})

# Keywords that indicate prohibited output (diagnosis / prescription)
PROHIBITED_KEYWORDS = frozenset({
    "diagnos", "prescri", "medicat", "treatment", "cure",
    "disease", "disorder", "syndrome", "condition is",
    "you have", "you are suffering", "recommend taking",
    "dosage", "drug", "tablet", "capsule", "injection",
    "mg ", "mg,", "ml ", "ml,",
})


class NextQuestionDecision(BaseModel):
    """Structured LLM output for adaptive next-question selection.

    Advisory only — ``QuestionService`` independently re-validates every field
    against the session's workflow and known facts before anything reaches the
    patient.
    """
    action: Literal["ASK", "COMPLETE"] = "ASK"
    # If action == ASK:
    question: Optional[str] = None
    question_type: Optional[str] = None  # TEXT | NUMBER | YES_NO | SINGLE_CHOICE
    question_code: Optional[str] = None  # Prefer existing DB question code if applicable
    category: Optional[str] = None
    reason: Optional[str] = None  # Internal — logged but never sent to patient


class ExtractedFact(BaseModel):
    """One normalized clinical key/value pair extracted from a patient answer."""
    key: str = Field(description="snake_case fact name, e.g. location, appetite, response")
    value: str = Field(description="normalized value, e.g. 'upper abdomen', 'reduced', 'yes'")


class SymptomDetail(BaseModel):
    """One symptom with the timing and severity that belong to THAT symptom.

    Keeping timing attached per-symptom is what stops "stomach pain for 3 days,
    with vomiting since yesterday" from collapsing into a single flat bag where
    the duration of one symptom gets attached to the other.
    """
    symptom: str = Field(description="normalized English symptom name, e.g. 'stomach pain'")
    duration: Optional[str] = Field(
        default=None,
        description="how long this symptom has lasted, e.g. '3 days'. Null if not stated.",
    )
    onset: Optional[str] = Field(
        default=None,
        description="when this symptom began, e.g. '1 day' for 'since yesterday'. Null if not stated.",
    )
    severity: Optional[str] = Field(
        default=None,
        description="severity of THIS symptom as the patient described it, e.g. 'severe'. Null if not stated.",
    )


class AnswerExtraction(BaseModel):
    """Structured LLM output for answer normalization.

    The clinical shape (primary vs associated symptoms) is modelled explicitly
    rather than as a flat key/value bag, because a flat bag cannot express which
    symptom a duration belongs to.
    """
    primary_complaint: Optional[SymptomDetail] = Field(
        default=None,
        description="The single main problem the patient is presenting with. Null if the answer names no symptom.",
    )
    associated_symptoms: list[SymptomDetail] = Field(
        default_factory=list,
        description="Additional symptoms mentioned alongside the primary complaint, each with its own timing.",
    )
    progression: Optional[str] = Field(
        default=None,
        description=(
            "How the condition is changing over time, ONLY if the patient stated a "
            "direction: 'improving', 'worsening', 'unchanged' or 'fluctuating'. "
            "Null otherwise. Never infer this from a duration or date."
        ),
    )
    facts: list[ExtractedFact] = Field(
        default_factory=list,
        description="Any other clinical facts that are not a symptom, e.g. location, appetite, sleep, a yes/no response.",
    )
    # MUST be drawn from the workflow category vocabulary supplied in the
    # prompt. Values outside that vocabulary are dropped by the backend.
    categories_satisfied: list[str] = Field(default_factory=list)
    confidence: Optional[float] = None

    # ── Derived views used by the backend ─────────────────────────────────

    @property
    def facts_dict(self) -> dict[str, str]:
        """Canonical FLAT fact map used for category-evidence checks.

        Derived from the PRIMARY complaint, the stated progression, and any other
        facts. Associated symptoms are deliberately excluded: the workflow's
        ONSET / SEVERITY questions are about the chief complaint, so "vomiting
        since yesterday" must not satisfy the onset of an undated stomach pain.
        """
        out: dict[str, str] = {}
        primary = self.primary_complaint
        if primary:
            if primary.symptom and primary.symptom.strip():
                out["symptom"] = primary.symptom.strip()
            if primary.duration and primary.duration.strip():
                out["duration"] = primary.duration.strip()
            if primary.onset and primary.onset.strip():
                out["onset"] = primary.onset.strip()
            if primary.severity and primary.severity.strip():
                out["severity"] = primary.severity.strip()
        if self.progression and self.progression.strip():
            out["progression"] = self.progression.strip()
        for fact in self.facts:
            key = (fact.key or "").strip()
            value = (fact.value or "").strip()
            # Never let a generic fact silently overwrite a structured slot.
            if key and value and key not in out:
                out[key] = value
        return out

    @property
    def clinical_block(self) -> dict[str, Any]:
        """Structured clinical shape persisted under the ``clinical`` envelope key."""
        return {
            "primary_complaint": (
                self.primary_complaint.model_dump() if self.primary_complaint else None
            ),
            "associated_symptoms": [s.model_dump() for s in self.associated_symptoms],
            "progression": self.progression or None,
        }

    @property
    def has_content(self) -> bool:
        """True when the extraction carries anything worth persisting."""
        return bool(
            self.primary_complaint
            or self.associated_symptoms
            or self.progression
            or self.facts
        )

    @property
    def bounded_confidence(self) -> Optional[float]:
        """Confidence clamped to [0, 1]; None when the model omitted it.

        Clamped rather than rejected: a model returning 1.2 is a formatting
        slip, not a reason to discard a good extraction.
        """
        if self.confidence is None:
            return None
        return max(0.0, min(1.0, float(self.confidence)))
