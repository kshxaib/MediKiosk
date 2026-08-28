"""Configuration and Master Data service for Streams, Departments, and Languages."""
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.hospital import Hospital
from app.models.medical_stream import MedicalStream
from app.schemas.language import LanguageRead

# Supported kiosk UI / clinical languages
SUPPORTED_LANGUAGES = [
    LanguageRead(code="en", name="English", native_name="English", is_default=True, is_active=True),
    LanguageRead(code="hi", name="Hindi", native_name="हिन्दी", is_default=False, is_active=True),
]


class ConfigService:
    @staticmethod
    def get_streams(db: Session) -> list[MedicalStream]:
        stmt = select(MedicalStream).where(MedicalStream.is_active.is_(True)).order_by(MedicalStream.created_at)
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_stream(db: Session, stream_id: uuid.UUID) -> Optional[MedicalStream]:
        return db.get(MedicalStream, stream_id)

    @staticmethod
    def get_departments(
        db: Session,
        hospital_id: Optional[uuid.UUID] = None,
        stream_code: Optional[str] = None,
    ) -> list[Department]:
        stmt = select(Department).where(Department.is_active.is_(True))
        if hospital_id:
            stmt = stmt.where(Department.hospital_id == hospital_id)
        if stream_code:
            stmt = stmt.where(Department.stream_code == stream_code)
        stmt = stmt.order_by(Department.name)
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_department(db: Session, department_id: uuid.UUID) -> Optional[Department]:
        return db.get(Department, department_id)

    @staticmethod
    def get_languages() -> list[LanguageRead]:
        return SUPPORTED_LANGUAGES
