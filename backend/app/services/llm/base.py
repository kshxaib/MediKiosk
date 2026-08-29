"""Abstract LLM service base — allows future provider swapping."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Optional

from app.services.llm.schemas import AnswerExtraction, ClinicalContext, NextQuestionDecision


class LLMUnavailableError(Exception):
    """Raised when the LLM provider is unavailable or returns invalid output.

    The interview services catch this and use the deterministic fallback.
    NEVER expose the raw exception message to patients.
    """


class BaseLLMService(ABC):
    """Provider-agnostic LLM service interface.

    Implementations must never let a provider-specific exception escape; wrap
    everything in ``LLMUnavailableError`` so callers can fall back safely.
    """

    @abstractmethod
    def decide_next_question(
        self,
        ctx: ClinicalContext,
    ) -> NextQuestionDecision:
        """Return a validated NextQuestionDecision or raise LLMUnavailableError.

        The returned decision is ADVISORY. The caller re-validates it against
        the session's workflow and known facts before showing anything.
        """

    @abstractmethod
    def extract_answer(
        self,
        raw_answer: str,
        question_text: str,
        question_type: str,
        allowed_categories: Sequence[str],
        question_category: Optional[str] = None,
    ) -> AnswerExtraction:
        """Return structured AnswerExtraction or raise LLMUnavailableError.

        ``allowed_categories`` is the category vocabulary of the session's own
        clinical workflow. The model must map facts onto it rather than
        inventing category names; the caller drops anything outside it.
        """
