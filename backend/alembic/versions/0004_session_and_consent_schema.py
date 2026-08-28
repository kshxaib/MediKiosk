"""session, consent, hospital, stream, department schema

Revision ID: 0004_session_and_consent_schema
Revises: 0003_patient_identity_schema
Create Date: 2026-08-28

Phase 4 Session and Consent:
- hospitals: Facility information
- medical_streams: Modern Medicine vs AYUSH streams
- departments: Clinical departments per hospital (GEN_MED, CARDIO, NEURO, ORTHO, DERMA, AYURVEDA)
- intake_sessions: Patient intake consultation session state machine
- consents: Explicit timestamped patient consent records
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "0004_session_and_consent_schema"
down_revision: Union[str, None] = "0003_patient_identity_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create hospitals table
    op.create_table(
        "hospitals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), server_default="India", nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_hospitals_code", "hospitals", ["code"], unique=True)

    # 2. Create medical_streams table
    op.create_table(
        "medical_streams",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_medical_streams_code", "medical_streams", ["code"], unique=True)

    # 3. Create departments table
    op.create_table(
        "departments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("hospital_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("stream_code", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["hospital_id"],
            ["hospitals.id"],
            name="fk_departments_hospital_id_hospitals",
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_departments_hospital_id", "departments", ["hospital_id"], unique=False)
    op.create_index("ix_departments_code", "departments", ["code"], unique=False)
    op.create_index("ix_departments_stream_code", "departments", ["stream_code"], unique=False)

    # 4. Create intake_sessions table
    op.create_table(
        "intake_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), nullable=False),
        sa.Column("hospital_id", UUID(as_uuid=True), nullable=False),
        sa.Column("medical_stream_id", UUID(as_uuid=True), nullable=True),
        sa.Column("department_id", UUID(as_uuid=True), nullable=True),
        sa.Column("language", sa.String(length=10), server_default="en", nullable=False),
        sa.Column("status", sa.String(length=50), server_default="CREATED", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            name="fk_intake_sessions_patient_id_patients",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["hospital_id"],
            ["hospitals.id"],
            name="fk_intake_sessions_hospital_id_hospitals",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["medical_stream_id"],
            ["medical_streams.id"],
            name="fk_intake_sessions_medical_stream_id_medical_streams",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
            name="fk_intake_sessions_department_id_departments",
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_intake_sessions_patient_id", "intake_sessions", ["patient_id"], unique=False)
    op.create_index("ix_intake_sessions_hospital_id", "intake_sessions", ["hospital_id"], unique=False)
    op.create_index("ix_intake_sessions_medical_stream_id", "intake_sessions", ["medical_stream_id"], unique=False)
    op.create_index("ix_intake_sessions_department_id", "intake_sessions", ["department_id"], unique=False)
    op.create_index("ix_intake_sessions_status", "intake_sessions", ["status"], unique=False)

    # 5. Create consents table
    op.create_table(
        "consents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", UUID(as_uuid=True), nullable=False),
        sa.Column("patient_id", UUID(as_uuid=True), nullable=False),
        sa.Column("consent_type", sa.String(length=50), server_default="CLINICAL_INTAKE", nullable=False),
        sa.Column("consent_text", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=10), server_default="en", nullable=False),
        sa.Column("is_granted", sa.Boolean(), nullable=False),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["intake_sessions.id"],
            name="fk_consents_session_id_intake_sessions",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            name="fk_consents_patient_id_patients",
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_consents_session_id", "consents", ["session_id"], unique=False)
    op.create_index("ix_consents_patient_id", "consents", ["patient_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_consents_patient_id", table_name="consents")
    op.drop_index("ix_consents_session_id", table_name="consents")
    op.drop_table("consents")

    op.drop_index("ix_intake_sessions_status", table_name="intake_sessions")
    op.drop_index("ix_intake_sessions_department_id", table_name="intake_sessions")
    op.drop_index("ix_intake_sessions_medical_stream_id", table_name="intake_sessions")
    op.drop_index("ix_intake_sessions_hospital_id", table_name="intake_sessions")
    op.drop_index("ix_intake_sessions_patient_id", table_name="intake_sessions")
    op.drop_table("intake_sessions")

    op.drop_index("ix_departments_stream_code", table_name="departments")
    op.drop_index("ix_departments_code", table_name="departments")
    op.drop_index("ix_departments_hospital_id", table_name="departments")
    op.drop_table("departments")

    op.drop_index("ix_medical_streams_code", table_name="medical_streams")
    op.drop_table("medical_streams")

    op.drop_index("ix_hospitals_code", table_name="hospitals")
    op.drop_table("hospitals")
