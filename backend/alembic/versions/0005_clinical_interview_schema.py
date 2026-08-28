"""clinical workflows, questions, and answers schema

Revision ID: 0005_clinical_interview_schema
Revises: 0004_session_and_consent_schema
Create Date: 2026-08-28

Phase 5A Clinical Interview Foundation:
- clinical_workflows: Configurable stream and department clinical intake workflows
- questions: Workflow questions with category, sequence, question type, options, validation rules
- answers: Clinically meaningful patient responses with raw and normalized JSONB payload
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "0005_clinical_interview_schema"
down_revision: Union[str, None] = "0004_session_and_consent_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create clinical_workflows table
    op.create_table(
        "clinical_workflows",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("medical_stream_id", UUID(as_uuid=True), nullable=False),
        sa.Column("department_id", UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("version", sa.String(length=50), server_default="1.0.0", nullable=False),
        sa.Column("configuration_json", JSONB(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["medical_stream_id"],
            ["medical_streams.id"],
            name="fk_clinical_workflows_medical_stream_id_medical_streams",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
            name="fk_clinical_workflows_department_id_departments",
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_clinical_workflows_code", "clinical_workflows", ["code"], unique=True)
    op.create_index("ix_clinical_workflows_medical_stream_id", "clinical_workflows", ["medical_stream_id"], unique=False)
    op.create_index("ix_clinical_workflows_department_id", "clinical_workflows", ["department_id"], unique=False)

    # 2. Create questions table
    op.create_table(
        "questions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_id", UUID(as_uuid=True), nullable=False),
        sa.Column("question_code", sa.String(length=100), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=50), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("sequence", sa.Integer(), server_default="1", nullable=True),
        sa.Column("is_required", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("language", sa.String(length=10), server_default="en", nullable=False),
        sa.Column("validation_rules", JSONB(), nullable=True),
        sa.Column("options", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["clinical_workflows.id"],
            name="fk_questions_workflow_id_clinical_workflows",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("workflow_id", "language", "question_code", name="uq_questions_workflow_lang_code"),
    )
    op.create_index("ix_questions_workflow_id", "questions", ["workflow_id"], unique=False)
    op.create_index("ix_questions_question_code", "questions", ["question_code"], unique=False)
    op.create_index("ix_questions_category", "questions", ["category"], unique=False)
    op.create_index("ix_questions_language", "questions", ["language"], unique=False)

    # 3. Create answers table
    op.create_table(
        "answers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", UUID(as_uuid=True), nullable=True),
        sa.Column("patient_id", UUID(as_uuid=True), nullable=False),
        sa.Column("raw_answer", sa.Text(), nullable=True),
        sa.Column("normalized_answer", JSONB(), nullable=True),
        sa.Column("answer_type", sa.String(length=50), nullable=False),
        sa.Column("source", sa.String(length=50), server_default="TOUCH", nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_patient_corrected", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["intake_sessions.id"],
            name="fk_answers_session_id_intake_sessions",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
            name="fk_answers_question_id_questions",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            name="fk_answers_patient_id_patients",
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_answers_session_id", "answers", ["session_id"], unique=False)
    op.create_index("ix_answers_question_id", "answers", ["question_id"], unique=False)
    op.create_index("ix_answers_patient_id", "answers", ["patient_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_answers_patient_id", table_name="answers")
    op.drop_index("ix_answers_question_id", table_name="answers")
    op.drop_index("ix_answers_session_id", table_name="answers")
    op.drop_table("answers")

    op.drop_index("ix_questions_language", table_name="questions")
    op.drop_index("ix_questions_category", table_name="questions")
    op.drop_index("ix_questions_question_code", table_name="questions")
    op.drop_index("ix_questions_workflow_id", table_name="questions")
    op.drop_table("questions")

    op.drop_index("ix_clinical_workflows_department_id", table_name="clinical_workflows")
    op.drop_index("ix_clinical_workflows_medical_stream_id", table_name="clinical_workflows")
    op.drop_index("ix_clinical_workflows_code", table_name="clinical_workflows")
    op.drop_table("clinical_workflows")
