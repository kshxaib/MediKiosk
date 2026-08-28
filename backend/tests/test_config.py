"""Tests for GET /api/v1/config/public."""
from fastapi.testclient import TestClient


def test_public_config_returns_non_secret_fields(client: TestClient) -> None:
    response = client.get("/api/v1/config/public")

    assert response.status_code == 200
    body = response.json()
    assert body["app_name"] == "MediKiosk"
    assert body["api_version"]
    assert body["environment"]


def test_public_config_leaks_no_secrets(client: TestClient) -> None:
    response = client.get("/api/v1/config/public")
    serialized = str(response.json()).lower()

    for forbidden in ("secret", "password", "api_key", "database_url", "jwt"):
        assert forbidden not in serialized
