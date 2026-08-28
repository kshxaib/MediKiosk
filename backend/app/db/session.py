"""Database engine and session factory.

Creating the engine does not open a connection; ``pool_pre_ping`` validates
connections on checkout so a dropped Postgres connection is recovered
transparently. Request-scoped sessions are provided via ``app.api.deps.get_db``.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
