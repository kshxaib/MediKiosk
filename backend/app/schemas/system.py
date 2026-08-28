"""Pydantic schemas for the system endpoints."""
from datetime import datetime

from pydantic import BaseModel


class HealthChecks(BaseModel):
    database: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    timestamp: datetime
    checks: HealthChecks


class PublicConfig(BaseModel):
    """Non-secret configuration safe to expose to any client."""

    app_name: str
    environment: str
    api_version: str
