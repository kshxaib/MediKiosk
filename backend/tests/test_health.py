"""Tests for GET /api/v1/health.

The DB session dependency is overridden with fakes so both the healthy and
degraded paths are covered without a real database.
"""
from collections.abc import Iterator

from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.main import app


class _OkSession:
    def execute(self, *_args: object, **_kwargs: object) -> None:
        return None

    def close(self) -> None:
        pass


class _FailingSession:
    def execute(self, *_args: object, **_kwargs: object) -> None:
        raise RuntimeError("database unavailable")

    def close(self) -> None:
        pass


def _ok_db() -> Iterator[_OkSession]:
    yield _OkSession()


def _failing_db() -> Iterator[_FailingSession]:
    yield _FailingSession()


def test_health_ok(client: TestClient) -> None:
    app.dependency_overrides[get_db] = _ok_db
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["checks"]["database"] == "ok"
    assert body["service"] == "MediKiosk"


def test_health_reports_503_when_db_down(client: TestClient) -> None:
    app.dependency_overrides[get_db] = _failing_db
    response = client.get("/api/v1/health")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unhealthy"
    assert body["checks"]["database"] == "unavailable"
