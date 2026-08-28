"""Aggregates all v1 routers under the ``/api/v1`` prefix."""
from fastapi import APIRouter

from app.api.v1.endpoints import config, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(config.router)
