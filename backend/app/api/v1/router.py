"""Aggregates all v1 routers under the ``/api/v1`` prefix."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    cases,
    config,
    departments,
    doctor,
    health,
    identity,
    interview,
    languages,
    patients,
    sessions,
    streams,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(config.router)
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(doctor.router)
api_router.include_router(patients.router)
api_router.include_router(identity.router)
api_router.include_router(languages.router)
api_router.include_router(streams.router)
api_router.include_router(departments.router)
api_router.include_router(sessions.router)
api_router.include_router(interview.router)
api_router.include_router(cases.router)
