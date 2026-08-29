"""Clinical fact and category reasoning for the adaptive questioning engine.

This module is the single source of truth for the question that Phase 5B got
wrong: *is the information this question asks for already known?*

Design constraints:
  - MULTI-HOSPITAL SAFE. Nothing here reads global state. Every decision is
    made from (a) the questions belonging to the session's own workflow and
    (b) the Answer rows belonging to the session itself.
  - CONFIGURABLE, not hardcoded. Sensible clinical defaults live here, but any
    workflow may override them through the existing (previously unused)
    ``clinical_workflows.configuration_json`` JSONB column, so no migration is
    needed to tune behaviour per hospital / stream / department.
  - The LLM is advisory. Everything it proposes is re-checked here.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional

from app.services.llm.schemas import PROHIBITED_KEYWORDS

# ─── Category canonicalisation ────────────────────────────────────────────────
# Different workflows (and the LLM) name the same clinical slot differently.
# "When did the pain start?" (ONSET) and "How long have you had this pain?"
# (DURATION) target the same information, so they must collapse to one token.
_DEFAULT_EQUIVALENCE: dict[str, str] = {
    # Chief complaint
    "CHIEF_COMPLAINT": "CHIEF_COMPLAINT",
    "COMPLAINT": "CHIEF_COMPLAINT",
    "PRESENTING_COMPLAINT": "CHIEF_COMPLAINT",
    "PRIMARY_CONCERN": "CHIEF_COMPLAINT",
    "SYMPTOM": "CHIEF_COMPLAINT",
    "SYMPTOMS": "CHIEF_COMPLAINT",
    # Onset / duration
    "ONSET": "ONSET",
    "DURATION": "ONSET",
    "ONSET_DURATION": "ONSET",
    "SYMPTOM_DURATION": "ONSET",
    "TIMING": "ONSET",
    "SINCE_WHEN": "ONSET",
    # Severity
    "SEVERITY": "SEVERITY",
    "PAIN_SEVERITY": "SEVERITY",
    "PAIN_SCORE": "SEVERITY",
    "INTENSITY": "SEVERITY",
    # Fever
    "FEVER_CHECK": "FEVER_CHECK",
    "FEVER": "FEVER_CHECK",
    "TEMPERATURE": "FEVER_CHECK",
    # Course over time
    "PROGRESSION": "PROGRESSION",
    "COURSE": "PROGRESSION",
    "TREND": "PROGRESSION",
    # Site
    "LOCATION": "LOCATION",
    "SITE": "LOCATION",
    # AYUSH / Ayurveda
    "AGNI": "AGNI",
    "APPETITE": "AGNI",
    "DIGESTION": "AGNI",
    "NIDRA": "NIDRA",
    "SLEEP": "NIDRA",
    "VATA_CHECK": "VATA_CHECK",
    "VATA": "VATA_CHECK",
}

# Fact keys that imply a category, used as a defensive secondary signal when
# the extractor reports a fact but forgets to list the matching category.
# Matched as substrings of the normalized fact key, so "severity_1" and
# "symptom_2" both resolve correctly.
_DEFAULT_FACT_KEY_TOKENS: dict[str, tuple[str, ...]] = {
    "CHIEF_COMPLAINT": ("symptom", "complaint", "concern", "problem", "issue"),
    "ONSET": ("onset", "duration", "since", "started", "start_", "how_long", "days", "weeks", "months"),
    "SEVERITY": ("severity", "intensity", "pain_score", "pain_level", "severe"),
    "FEVER_CHECK": ("fever", "temperature", "chills", "pyrexia"),
    "PROGRESSION": ("progression", "trend", "course", "worsening", "improving"),
    "LOCATION": ("location", "site", "region", "where"),
    "AGNI": ("agni", "appetite", "digestion", "digestive"),
    "NIDRA": ("nidra", "sleep"),
    "VATA_CHECK": ("vata", "stiffness", "dryness", "cracking"),
}

_YES_TOKENS = frozenset({"yes", "y", "true", "haan", "ha", "yeah", "yep", "affirmative", "present"})
_NO_TOKENS = frozenset({"no", "n", "false", "nahi", "nope", "negative", "absent", "none"})
_UNSURE_TOKENS = frozenset({"not sure", "notsure", "unsure", "unknown", "maybe", "dont know", "don't know"})

# Equivalent surface forms for closed-choice values. The extraction prompt asks
# the model for canonical values ("worsening"), while a workflow's option list
# may spell the same thing differently ("Getting Worse"). Without this, a stated
# progression would fail the option match and the patient would be asked to pick
# from a list they had already effectively answered.
_DEFAULT_VALUE_SYNONYMS: tuple[tuple[str, ...], ...] = (
    ("worsening", "getting worse", "worse", "deteriorating", "increasing"),
    ("improving", "getting better", "better", "improved", "decreasing"),
    ("unchanged", "staying about the same", "about the same", "the same", "same",
     "no change", "stable", "steady"),
    ("fluctuating", "comes and goes", "on and off", "intermittent", "variable"),
)

_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
_WS_RE = re.compile(r"\s+")

# Max length of a patient-derived value echoed back into a kiosk question.
MAX_ECHO_LENGTH = 80


def normalize_category(raw: Optional[str]) -> Optional[str]:
    """Uppercase/underscore a raw category label without applying equivalence."""
    if not raw:
        return None
    token = _WS_RE.sub("_", str(raw).strip()).upper()
    token = re.sub(r"[^A-Z0-9_]", "_", token)
    token = re.sub(r"_+", "_", token).strip("_")
    return token or None


@dataclass(frozen=True)
class ClinicalPolicy:
    """Per-workflow rules for category equivalence and fact sufficiency."""

    equivalence: dict[str, str]
    fact_key_tokens: dict[str, tuple[str, ...]]
    value_synonyms: tuple[tuple[str, ...], ...] = _DEFAULT_VALUE_SYNONYMS
    infer_from_fact_keys: bool = True
    numeric_refinement: bool = True
    # When True, an extractor's claim that a category is satisfied is only
    # honoured if an actual fact value backs it. Guards against the model
    # over-claiming: "vomiting since yesterday" does not state whether the
    # condition is improving or worsening, so PROGRESSION must stay unanswered
    # even if the model lists it.
    require_fact_evidence: bool = True

    # ── Category resolution ──────────────────────────────────────────────
    def canonical(self, raw: Optional[str]) -> Optional[str]:
        """Map any category spelling onto its canonical token."""
        token = normalize_category(raw)
        if not token:
            return None
        return self.equivalence.get(token, token)

    def canonical_set(self, raws: Any) -> set[str]:
        if not raws:
            return set()
        out: set[str] = set()
        for raw in raws:
            token = self.canonical(raw)
            if token:
                out.add(token)
        return out

    def categories_for_fact_key(self, fact_key: str) -> set[str]:
        """Infer categories implied by a fact key (secondary signal)."""
        if not self.infer_from_fact_keys or not fact_key:
            return set()
        key = normalize_category(fact_key)
        if not key:
            return set()
        lowered = key.lower()
        return {
            category
            for category, tokens in self.fact_key_tokens.items()
            if any(tok in lowered for tok in tokens)
        }

    def fact_value_for_category(
        self, facts: dict[str, Any], category: Optional[str]
    ) -> Optional[str]:
        """Return the known fact value that satisfies ``category``, if any."""
        target = self.canonical(category)
        if not target or not facts:
            return None
        for key, value in facts.items():
            if value in (None, ""):
                continue
            if target in self.categories_for_fact_key(str(key)):
                return str(value)
        return None

    def is_category_substantiated(
        self, facts: dict[str, Any], category: Optional[str]
    ) -> bool:
        """Is an extractor's claim that ``category`` is satisfied backed by a fact?

        A model may list a category it merely inferred. Without a supporting fact
        value the claim is unsubstantiated and the category must remain
        genuinely missing, not be demoted to a refinement.

        Returns True unconditionally when evidence checking is disabled, or when
        fact-key inference is off (in which case evidence cannot be evaluated and
        the extractor's claim is the only signal available).
        """
        if not self.require_fact_evidence or not self.infer_from_fact_keys:
            return True
        return self.fact_value_for_category(facts, category) is not None

    # ── Sufficiency ──────────────────────────────────────────────────────
    def is_value_sufficient(self, question: Any, value: Optional[str]) -> bool:
        """Can ``value`` stand in for a real answer to ``question``?

        A qualitative "severe" satisfies the SEVERITY *category*, but it is NOT
        a numeric 1-10 score. When the question demands a shape the known value
        does not have, the category counts as partially known and the caller
        should ask a refinement question instead of skipping.
        """
        if value is None or not str(value).strip():
            return False

        text = str(value).strip()
        q_type = (getattr(question, "question_type", None) or "TEXT").upper()

        if q_type == "NUMBER":
            if not self.numeric_refinement:
                return True
            match = _NUMBER_RE.search(text)
            if not match:
                return False
            number = float(match.group())
            rules = getattr(question, "validation_rules", None) or {}
            minimum, maximum = rules.get("min"), rules.get("max")
            if minimum is not None and number < float(minimum):
                return False
            if maximum is not None and number > float(maximum):
                return False
            return True

        if q_type == "YES_NO":
            return _match_yes_no(text) is not None

        if q_type in ("SINGLE_CHOICE", "MULTI_CHOICE"):
            return self.match_option(text, getattr(question, "options", None)) is not None

        # TEXT / VOICE / DATE and anything else: any non-empty value is enough.
        return True

    def match_option(self, text: str, options: Any) -> Optional[str]:
        """Resolve a known value onto one of a question's options, if possible.

        Tries a direct/substring match first, then equivalent surface forms, so
        a canonical "worsening" resolves to a "Getting Worse" option.
        """
        direct = _match_option(text, options)
        if direct is not None:
            return direct
        if not options or not isinstance(options, (list, tuple)):
            return None
        lowered = text.strip().lower()
        for group in self.value_synonyms:
            if not any(lowered == form or form in lowered for form in group):
                continue
            for option in options:
                opt = str(option).strip().lower()
                if not opt:
                    continue
                if any(form == opt or form in opt or opt in form for form in group):
                    return str(option)
        return None


def _match_yes_no(text: str) -> Optional[str]:
    lowered = text.strip().lower()
    if lowered in _YES_TOKENS:
        return "YES"
    if lowered in _NO_TOKENS:
        return "NO"
    if lowered in _UNSURE_TOKENS:
        return "NOT SURE"
    return None


def _match_option(text: str, options: Any) -> Optional[str]:
    if not options or not isinstance(options, (list, tuple)):
        return None
    lowered = text.strip().lower()
    for option in options:
        opt = str(option).strip().lower()
        if not opt:
            continue
        if lowered == opt or lowered in opt or opt in lowered:
            return str(option)
    return None


# ─── Policy construction ──────────────────────────────────────────────────────

DEFAULT_POLICY = ClinicalPolicy(
    equivalence=dict(_DEFAULT_EQUIVALENCE),
    fact_key_tokens={k: tuple(v) for k, v in _DEFAULT_FACT_KEY_TOKENS.items()},
)


def policy_for_workflow(workflow: Any) -> ClinicalPolicy:
    """Build the clinical policy for one workflow.

    Reads optional overrides from ``workflow.configuration_json`` under the
    ``clinical_policy`` key. Malformed configuration is ignored rather than
    raised: a bad override must never take the kiosk down.
    """
    config = getattr(workflow, "configuration_json", None) or {}
    raw = config.get("clinical_policy") if isinstance(config, dict) else None
    if not isinstance(raw, dict):
        return DEFAULT_POLICY

    equivalence = dict(_DEFAULT_EQUIVALENCE)
    extra_equiv = raw.get("category_equivalence")
    if isinstance(extra_equiv, dict):
        for alias, canonical in extra_equiv.items():
            alias_token = normalize_category(alias)
            canonical_token = normalize_category(canonical)
            if alias_token and canonical_token:
                equivalence[alias_token] = canonical_token

    fact_keys = {k: tuple(v) for k, v in _DEFAULT_FACT_KEY_TOKENS.items()}
    extra_keys = raw.get("category_fact_keys")
    if isinstance(extra_keys, dict):
        for category, tokens in extra_keys.items():
            category_token = normalize_category(category)
            if category_token and isinstance(tokens, (list, tuple)):
                fact_keys[category_token] = tuple(
                    str(t).strip().lower() for t in tokens if str(t).strip()
                )

    value_synonyms = _DEFAULT_VALUE_SYNONYMS
    extra_synonyms = raw.get("value_synonyms")
    if isinstance(extra_synonyms, list):
        parsed = tuple(
            tuple(str(form).strip().lower() for form in group if str(form).strip())
            for group in extra_synonyms
            if isinstance(group, (list, tuple)) and len(group) > 1
        )
        if parsed:
            value_synonyms = _DEFAULT_VALUE_SYNONYMS + parsed

    return ClinicalPolicy(
        equivalence=equivalence,
        fact_key_tokens=fact_keys,
        value_synonyms=value_synonyms,
        infer_from_fact_keys=bool(raw.get("infer_categories_from_fact_keys", True)),
        numeric_refinement=bool(raw.get("numeric_refinement", True)),
        require_fact_evidence=bool(raw.get("require_fact_evidence", True)),
    )


# ─── Patient-facing echo safety ───────────────────────────────────────────────

def sanitize_echo(value: Optional[str]) -> Optional[str]:
    """Make a patient-derived value safe to echo back into a kiosk question.

    The value originated in untrusted patient text (via LLM extraction), so it
    is stripped of control characters, whitespace-collapsed, length-capped, and
    rejected outright if it contains prohibited clinical assertion content.
    Returns None when the value must not be echoed.
    """
    if value is None:
        return None
    text = _WS_RE.sub(" ", _CONTROL_RE.sub(" ", str(value))).strip()
    if not text:
        return None
    if len(text) > MAX_ECHO_LENGTH:
        return None
    lowered = text.lower()
    if any(kw in lowered for kw in PROHIBITED_KEYWORDS):
        return None
    # Reject quote/brace characters that could break out of the echo context.
    if any(ch in text for ch in ('"', "{", "}", "<", ">", "\\")):
        return None
    return text


def build_refinement_question(question_text: str, known_value: Optional[str]) -> str:
    """Compose a confirmation/refinement question for a partially-known slot.

    Example:
        known_value = "severe"
        question_text = "How would you rate the severity ... 1 (mild) to 10 (severe)?"
        -> 'You mentioned it is "severe". To record this precisely — how would
            you rate the severity ... 1 (mild) to 10 (severe)?'

    Falls back to the plain question when the value cannot be safely echoed, so
    the patient is never shown unsanitized text.
    """
    base = (question_text or "").strip()
    safe = sanitize_echo(known_value)
    if not safe or not base:
        return base
    lowered_base = base[0].lower() + base[1:] if base else base
    return f'You mentioned it is "{safe}". To record this precisely — {lowered_base}'
