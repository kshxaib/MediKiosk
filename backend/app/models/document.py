"""Document and DocumentExtraction ORM models (Phase 5C data layer).

Field baseline: PROJECT_REQUIREMENT.md §36A.16 and §36A.18.

SCOPE NOTE
    Phase 5C creates the persistence layer only, because the case summary must
    read real historical medical information from somewhere. The INGESTION
    pipeline — Cloudinary upload, the OCR engine, and the LLM that populates
    DocumentExtraction — remains Phase 6. Nothing in Phase 5C writes these rows
    automatically; the summary reads whatever genuinely exists and reports the
    section as unavailable when nothing does.
"""
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.intake_session import IntakeSession
    from app.models.patient import Patient


class DocumentType(str, enum.Enum):
    PRESCRIPTION = "PRESCRIPTION"
    LAB_REPORT = "LAB_REPORT"
    DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY"
    INVESTIGATION = "INVESTIGATION"
    SURGERY_RECORD = "SURGERY_RECORD"
    OTHER = "OTHER"


class ExtractionStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Metadata + Cloudinary reference for one uploaded medical document.

    The binary itself never lives in PostgreSQL (§36C.2).
    """

    __tablename__ = "documents"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intake_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    uploaded_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    cloudinary_public_id: Mapped[str] = mapped_column(String(500), nullable=False)
    cloudinary_resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    cloudinary_format: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cloudinary_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    document_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    patient: Mapped["Patient"] = relationship("Patient")
    session: Mapped[Optional["IntakeSession"]] = relationship(
        "IntakeSession", back_populates="documents"
    )
    extraction: Mapped[Optional["DocumentExtraction"]] = relationship(
        "DocumentExtraction",
        back_populates="document",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<Document {self.document_type} patient={self.patient_id}>"


class DocumentExtraction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Structured medical information extracted from a document.

    Each JSONB column holds a list of objects, e.g.
        diagnoses:      [{"name": "Diabetes", "confidence": 0.94}]
        medications:    [{"name": "Metformin", "dose": "500 mg", "confidence": 0.91}]
        investigations: [{"name": "HbA1c", "value": "8.2%", "date": "2026-08-12"}]
    """

    __tablename__ = "document_extractions"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
    )
    diagnoses: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    medications: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    investigations: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    procedures: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    allergies: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    doctors: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    hospitals: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    dates: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    overall_confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    extraction_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    document: Mapped["Document"] = relationship("Document", back_populates="extraction")

    def __repr__(self) -> str:
        return f"<DocumentExtraction document={self.document_id} status={self.status}>"
