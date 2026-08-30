"""case summary schema: vitals, documents, timeline, alerts, cases

Revision ID: 0006_case_summary_schema
Revises: 0005_clinical_interview_schema
Create Date: 2026-08-30

Phase 5C Structured AI Case Summary.

The case summary must combine Patient Interview + Vitals + Previous Documents +
Timeline + Patient Corrections + Alerts. Phase 5A/5B supplied only the interview
half, so this migration adds the remaining requirement-defined tables
(PROJECT_REQUIREMENT.md §36A) that the summary reads from:

- vitals               §36A.15  -> "Vitals" section
- documents            §36A.16  -> "Previous Documents"
- document_extractions §36A.18  -> past medical / drug / investigation history
- timeline_events      §36A.19  -> "Timeline"
- alerts               §36A.20  -> "Alerts"
- cases                §36A.21  -> the structured summary container itself
- case_edits           §36A.23  -> patient corrections / doctor verification

Only the persistence layer is created here. The ingestion pipelines (Cloudinary
upload, OCR engine, document-extraction LLM, red-flag rule engine) remain
Phase 6/7 — the summary reports a section as unavailable when no rows exist
rather than fabricating content.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "0006_case_summary_schema"
down_revision: Union[str, None] = "0005_clinical_interview_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. vitals ─────────────────────────────────────────────────────────
    op.create_table(
        "vitals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", UUID(as_uuid=True), nullable=False),
        sa.Column("patient_id", UUID(as_uuid=True), nullable=False),
        sa.Column("weight_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("height_cm", sa.Numeric(6, 2), nullable=True),
        sa.Column("systolic_bp", sa.Integer(), nullable=True),
        sa.Column("diastolic_bp", sa.Integer(), nullable=True),
        sa.Column("pulse_bpm", sa.Integer(), nullable=True),
        sa.Column("temperature_c", sa.Numeric(5, 2), nullable=True),
        sa.Column("spo2_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("source", sa.String(length=50), server_default="MANUAL", nullable=False),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"], ["intake_sessions.id"],
            name="fk_vitals_session_id_intake_sessions", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"],
            name="fk_vitals_patient_id_patients", ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_vitals_session_id", "vitals", ["session_id"])
    op.create_index("ix_vitals_patient_id", "vitals", ["patient_id"])

    # ── 2. documents ──────────────────────────────────────────────────────
    op.create_table(
        "documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", UUID(as_uuid=True), nullable=True),
        sa.Column("uploaded_by", UUID(as_uuid=True), nullable=True),
        sa.Column("document_type", sa.String(length=50), nullable=False),
        sa.Column("original_filename", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("cloudinary_public_id", sa.String(length=500), nullable=False),
        sa.Column("cloudinary_resource_type", sa.String(length=50), nullable=False),
        sa.Column("cloudinary_format", sa.String(length=50), nullable=True),
        sa.Column("cloudinary_version", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("document_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"],
            name="fk_documents_patient_id_patients", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"], ["intake_sessions.id"],
            name="fk_documents_session_id_intake_sessions", ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"], ["users.id"],
            name="fk_documents_uploaded_by_users", ondelete="SET NULL",
        ),
    )
    op.create_index("ix_documents_patient_id", "documents", ["patient_id"])
    op.create_index("ix_documents_session_id", "documents", ["session_id"])
    op.create_index("ix_documents_document_type", "documents", ["document_type"])
    op.create_index("ix_documents_status", "documents", ["status"])

    # ── 3. document_extractions ───────────────────────────────────────────
    op.create_table(
        "document_extractions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", UUID(as_uuid=True), nullable=False),
        sa.Column("diagnoses", JSONB(), nullable=True),
        sa.Column("medications", JSONB(), nullable=True),
        sa.Column("investigations", JSONB(), nullable=True),
        sa.Column("procedures", JSONB(), nullable=True),
        sa.Column("allergies", JSONB(), nullable=True),
        sa.Column("doctors", JSONB(), nullable=True),
        sa.Column("hospitals", JSONB(), nullable=True),
        sa.Column("dates", JSONB(), nullable=True),
        sa.Column("overall_confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column("extraction_model", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"],
            name="fk_document_extractions_document_id_documents", ondelete="CASCADE",
        ),
        sa.UniqueConstraint("document_id", name="uq_document_extractions_document_id"),
    )
    op.create_index("ix_document_extractions_document_id", "document_extractions", ["document_id"])
    op.create_index("ix_document_extractions_status", "document_extractions", ["status"])

    # ── 4. timeline_events ────────────────────────────────────────────────
    op.create_table(
        "timeline_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", UUID(as_uuid=True), nullable=True),
        sa.Column("session_id", UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", UUID(as_uuid=True), nullable=True),
        sa.Column("confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"],
            name="fk_timeline_events_patient_id_patients", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"],
            name="fk_timeline_events_document_id_documents", ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"], ["intake_sessions.id"],
            name="fk_timeline_events_session_id_intake_sessions", ondelete="SET NULL",
        ),
    )
    op.create_index("ix_timeline_events_patient_id", "timeline_events", ["patient_id"])
    op.create_index("ix_timeline_events_document_id", "timeline_events", ["document_id"])
    op.create_index("ix_timeline_events_session_id", "timeline_events", ["session_id"])
    op.create_index("ix_timeline_events_event_type", "timeline_events", ["event_type"])
    op.create_index("ix_timeline_events_event_date", "timeline_events", ["event_date"])

    # ── 5. alerts ─────────────────────────────────────────────────────────
    op.create_table(
        "alerts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", UUID(as_uuid=True), nullable=False),
        sa.Column("patient_id", UUID(as_uuid=True), nullable=False),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=True),
        sa.Column("source_id", UUID(as_uuid=True), nullable=True),
        sa.Column("trigger_value", JSONB(), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="ACTIVE", nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"], ["intake_sessions.id"],
            name="fk_alerts_session_id_intake_sessions", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"],
            name="fk_alerts_patient_id_patients", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["acknowledged_by"], ["users.id"],
            name="fk_alerts_acknowledged_by_users", ondelete="SET NULL",
        ),
    )
    op.create_index("ix_alerts_session_id", "alerts", ["session_id"])
    op.create_index("ix_alerts_patient_id", "alerts", ["patient_id"])
    op.create_index("ix_alerts_alert_type", "alerts", ["alert_type"])
    op.create_index("ix_alerts_status", "alerts", ["status"])

    # ── 6. cases ──────────────────────────────────────────────────────────
    op.create_table(
        "cases",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", UUID(as_uuid=True), nullable=False),
        sa.Column("patient_id", UUID(as_uuid=True), nullable=False),
        sa.Column("hospital_id", UUID(as_uuid=True), nullable=False),
        sa.Column("medical_stream_id", UUID(as_uuid=True), nullable=True),
        sa.Column("department_id", UUID(as_uuid=True), nullable=True),
        sa.Column("chief_complaint", sa.Text(), nullable=True),
        sa.Column("summary", JSONB(), nullable=True),
        sa.Column("summary_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="DRAFT", nullable=False),
        sa.Column("generated_by_model", sa.String(length=100), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"], ["intake_sessions.id"],
            name="fk_cases_session_id_intake_sessions", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"],
            name="fk_cases_patient_id_patients", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["hospital_id"], ["hospitals.id"],
            name="fk_cases_hospital_id_hospitals", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["medical_stream_id"], ["medical_streams.id"],
            name="fk_cases_medical_stream_id_medical_streams", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["department_id"], ["departments.id"],
            name="fk_cases_department_id_departments", ondelete="RESTRICT",
        ),
        # §36B: one case per intake session.
        sa.UniqueConstraint("session_id", name="uq_cases_session_id"),
    )
    op.create_index("ix_cases_session_id", "cases", ["session_id"])
    op.create_index("ix_cases_patient_id", "cases", ["patient_id"])
    op.create_index("ix_cases_hospital_id", "cases", ["hospital_id"])
    op.create_index("ix_cases_medical_stream_id", "cases", ["medical_stream_id"])
    op.create_index("ix_cases_department_id", "cases", ["department_id"])
    op.create_index("ix_cases_status", "cases", ["status"])

    # ── 7. case_edits ─────────────────────────────────────────────────────
    op.create_table(
        "case_edits",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", UUID(as_uuid=True), nullable=False),
        sa.Column("edited_by", UUID(as_uuid=True), nullable=True),
        sa.Column("editor_type", sa.String(length=50), nullable=False),
        sa.Column("field_name", sa.String(length=255), nullable=False),
        sa.Column("old_value", JSONB(), nullable=True),
        sa.Column("new_value", JSONB(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["case_id"], ["cases.id"],
            name="fk_case_edits_case_id_cases", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["edited_by"], ["users.id"],
            name="fk_case_edits_edited_by_users", ondelete="SET NULL",
        ),
    )
    op.create_index("ix_case_edits_case_id", "case_edits", ["case_id"])
    op.create_index("ix_case_edits_editor_type", "case_edits", ["editor_type"])
    op.create_index("ix_case_edits_field_name", "case_edits", ["field_name"])


def downgrade() -> None:
    for idx, table in [
        ("ix_case_edits_field_name", "case_edits"),
        ("ix_case_edits_editor_type", "case_edits"),
        ("ix_case_edits_case_id", "case_edits"),
    ]:
        op.drop_index(idx, table_name=table)
    op.drop_table("case_edits")

    for idx in (
        "ix_cases_status", "ix_cases_department_id", "ix_cases_medical_stream_id",
        "ix_cases_hospital_id", "ix_cases_patient_id", "ix_cases_session_id",
    ):
        op.drop_index(idx, table_name="cases")
    op.drop_table("cases")

    for idx in (
        "ix_alerts_status", "ix_alerts_alert_type",
        "ix_alerts_patient_id", "ix_alerts_session_id",
    ):
        op.drop_index(idx, table_name="alerts")
    op.drop_table("alerts")

    for idx in (
        "ix_timeline_events_event_date", "ix_timeline_events_event_type",
        "ix_timeline_events_session_id", "ix_timeline_events_document_id",
        "ix_timeline_events_patient_id",
    ):
        op.drop_index(idx, table_name="timeline_events")
    op.drop_table("timeline_events")

    for idx in ("ix_document_extractions_status", "ix_document_extractions_document_id"):
        op.drop_index(idx, table_name="document_extractions")
    op.drop_table("document_extractions")

    for idx in (
        "ix_documents_status", "ix_documents_document_type",
        "ix_documents_session_id", "ix_documents_patient_id",
    ):
        op.drop_index(idx, table_name="documents")
    op.drop_table("documents")

    for idx in ("ix_vitals_patient_id", "ix_vitals_session_id"):
        op.drop_index(idx, table_name="vitals")
    op.drop_table("vitals")
