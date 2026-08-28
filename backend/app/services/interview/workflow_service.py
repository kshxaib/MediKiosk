"""Clinical Workflow retrieval and validation service."""
import uuid
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.clinical_workflow import ClinicalWorkflow
from app.models.department import Department
from app.models.medical_stream import MedicalStream


class WorkflowService:
    @staticmethod
    def get_active_workflow(
        db: Session,
        medical_stream_id: uuid.UUID,
        department_id: Optional[uuid.UUID] = None,
    ) -> ClinicalWorkflow:
        """
        Resolves the active clinical workflow for a stream and department.
        Prioritizes department-specific workflow, then falls back to stream-wide workflow.
        """
        # 1. Verify stream exists
        stream = db.get(MedicalStream, medical_stream_id)
        if not stream or not stream.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active medical stream with ID {medical_stream_id} not found",
            )

        # 2. If department specified, search for department-specific workflow
        if department_id:
            dept = db.get(Department, department_id)
            if not dept or not dept.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Active department with ID {department_id} not found",
                )

            stmt = select(ClinicalWorkflow).where(
                ClinicalWorkflow.medical_stream_id == medical_stream_id,
                ClinicalWorkflow.department_id == department_id,
                ClinicalWorkflow.is_active.is_(True),
            ).order_by(ClinicalWorkflow.created_at.desc())
            dept_workflow = db.scalars(stmt).first()
            if dept_workflow:
                return dept_workflow

        # 3. Fallback: stream-level general workflow
        stmt = select(ClinicalWorkflow).where(
            ClinicalWorkflow.medical_stream_id == medical_stream_id,
            ClinicalWorkflow.department_id.is_(None),
            ClinicalWorkflow.is_active.is_(True),
        ).order_by(ClinicalWorkflow.created_at.desc())
        stream_workflow = db.scalars(stmt).first()
        if stream_workflow:
            return stream_workflow

        # 4. Fallback: any active workflow under this stream
        stmt = select(ClinicalWorkflow).where(
            ClinicalWorkflow.medical_stream_id == medical_stream_id,
            ClinicalWorkflow.is_active.is_(True),
        ).order_by(ClinicalWorkflow.created_at.desc())
        any_workflow = db.scalars(stmt).first()
        if any_workflow:
            return any_workflow

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active clinical workflow configured for stream '{stream.name}'",
        )

    @staticmethod
    def get_workflows_for_stream(
        db: Session,
        medical_stream_id: uuid.UUID,
    ) -> list[ClinicalWorkflow]:
        stmt = select(ClinicalWorkflow).where(
            ClinicalWorkflow.medical_stream_id == medical_stream_id,
            ClinicalWorkflow.is_active.is_(True),
        ).order_by(ClinicalWorkflow.created_at)
        return list(db.scalars(stmt).all())
