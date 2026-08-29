"""Shared pytest fixtures.

Tests exercise the API through FastAPI's ``TestClient``.
"""
from collections.abc import Iterator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.services.llm import reset_llm_service


@pytest.fixture(autouse=True)
def disable_live_llm_for_unit_tests(request):
    """Disable live LLM network calls during unit/integration tests.

    Guarantees fast, deterministic execution. Tests that want the LLM path
    exercise it through an explicitly mocked service rather than the real
    provider. The live smoke test in test_llm_smoke.py bypasses this.
    """
    if "smoke" in request.node.name or "live_openai" in request.node.name:
        yield
        return

    reset_llm_service()
    with patch.object(settings, "OPENAI_API_KEY", ""):
        yield
    reset_llm_service()


@pytest.fixture()
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
