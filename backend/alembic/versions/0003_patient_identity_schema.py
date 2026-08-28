"""patient identity schema (patients, patient_identifiers, face_enrollments)

Revision ID: 0003_patient_identity_schema
Revises: 0002_staff_auth_schema
Create Date: 2026-08-28

Phase 3 patient identity:
- patients: Core patient entity with generated patient_code
- patient_identifiers: Polymorphic identifiers (MOBILE, future RFID)
- face_enrollments: Biometric ArcFace embedding references
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "0003_patient_identity_schema"
down_revision: Union[str, None] = "0002_staff_auth_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create patients table
    op.create_table(
        "patients",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_code", sa.String(length=20), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("primary_language", sa.String(length=10), nullable=True, server_default="en"),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_patients_patient_code", "patients", ["patient_code"], unique=True)

    # 2. Create patient_identifiers table
    op.create_table(
        "patient_identifiers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), nullable=False),
        sa.Column("identifier_type", sa.String(length=50), nullable=False),
        sa.Column("identifier_value", sa.String(length=255), nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            name="fk_patient_identifiers_patient_id_patients",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("identifier_type", "identifier_value", name="uq_patient_identifiers_type_value"),
    )
    op.create_index("ix_patient_identifiers_patient_id", "patient_identifiers", ["patient_id"], unique=False)
    op.create_index("ix_patient_identifiers_identifier_type", "patient_identifiers", ["identifier_type"], unique=False)
    op.create_index("ix_patient_identifiers_identifier_value", "patient_identifiers", ["identifier_value"], unique=False)

    # 3. Create face_enrollments table
    op.create_table(
        "face_enrollments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), nullable=False),
        sa.Column("embedding_reference", sa.Text(), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="ACTIVE", nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            name="fk_face_enrollments_patient_id_patients",
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_face_enrollments_patient_id", "face_enrollments", ["patient_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_face_enrollments_patient_id", table_name="face_enrollments")
    op.drop_table("face_enrollments")

    op.drop_index("ix_patient_identifiers_identifier_value", table_name="patient_identifiers")
    op.drop_index("ix_patient_identifiers_identifier_type", table_name="patient_identifiers")
    op.drop_index("ix_patient_identifiers_patient_id", table_name="patient_identifiers")
    op.drop_table("patient_identifiers")

    op.drop_index("ix_patients_patient_code", table_name="patients")
    op.drop_table("patients")
