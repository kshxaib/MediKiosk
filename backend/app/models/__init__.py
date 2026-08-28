"""SQLAlchemy ORM models.

Phase 1 intentionally defines NO business tables. Concrete models
(User, Patient, IntakeSession, ...) are introduced from Phase 2 onward per
PROJECT_REQUIREMENT.md's phased plan.

This package exists so Alembic autogenerate has a single, stable import target:
importing ``app.models`` must register every model on ``Base.metadata``. As
models are added, import them here.
"""
