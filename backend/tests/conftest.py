"""Shared pytest fixtures.

Tests exercise the API through FastAPI's ``TestClient``. The database
dependency is overridden per-test (see ``test_health``) so the suite does not
require a live Postgres instance.
"""
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
