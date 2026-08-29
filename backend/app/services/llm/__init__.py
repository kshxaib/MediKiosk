"""LLM service package (Phase 5B).

Exports:
    BaseLLMService      - Provider-neutral abstract interface
    OpenAIService       - OpenAI (default gpt-5-mini) via LangChain
    LLMUnavailableError - Raised when the provider fails; triggers fallback
    get_llm_service()   - Factory. Callers depend on this, not on a concrete
                          provider, so swapping providers touches one file.
"""
from __future__ import annotations

import logging
import threading
from typing import Optional

from app.core.config import settings
from app.services.llm.base import BaseLLMService, LLMUnavailableError
from app.services.llm.openai_service import OpenAIService

log = logging.getLogger(__name__)

_lock = threading.Lock()
_service: Optional[BaseLLMService] = None
# Config fingerprint the cached instance was built from. Deliberately excludes
# key material — only whether a key is present and which model is selected.
_fingerprint: Optional[tuple[bool, str]] = None


def _current_fingerprint() -> tuple[bool, str]:
    return (settings.llm_enabled, settings.OPENAI_MODEL)


def get_llm_service() -> BaseLLMService:
    """Return the configured LLM service.

    The instance is cached because constructing ``ChatOpenAI`` builds an HTTP
    client, and the previous implementation did that on every single request.
    The cache is invalidated automatically when the API-key presence or model
    name changes, so tests that patch settings get a correctly rebuilt service.

    Raises:
        LLMUnavailableError: when no API key is configured, or construction
            fails. Callers treat this as "use the deterministic engine".
    """
    global _service, _fingerprint

    if not settings.llm_enabled:
        raise LLMUnavailableError("No LLM API key is configured")

    fingerprint = _current_fingerprint()
    service = _service
    if service is not None and _fingerprint == fingerprint:
        return service

    with _lock:
        if _service is not None and _fingerprint == fingerprint:
            return _service
        try:
            _service = OpenAIService()
        except LLMUnavailableError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            log.warning(
                "LLM service construction failed",
                extra={"error_class": type(exc).__name__, "llm_success": False},
            )
            raise LLMUnavailableError("LLM service construction failed") from exc
        _fingerprint = fingerprint
        return _service


def reset_llm_service() -> None:
    """Drop the cached service. Used by tests and after a config reload."""
    global _service, _fingerprint
    with _lock:
        _service = None
        _fingerprint = None


__all__ = [
    "BaseLLMService",
    "LLMUnavailableError",
    "OpenAIService",
    "get_llm_service",
    "reset_llm_service",
]
