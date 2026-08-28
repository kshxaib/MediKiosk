"""Answer recording and clinical answer persistence service."""
import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.clinical_workflow import ClinicalWorkflow
from app.models.intake_session import IntakeSession, SessionStatus
from app.models.question import Question
from app.schemas.answer import AnswerCreate, AnswerSubmissionResponse
from app.services.interview.workflow_service import WorkflowService
from app.utils.datetime import utcnow


class AnswerService:
    @staticmethod
    def record_answer(
        db: Session,
        session_id: uuid.UUID,
        payload: AnswerCreate,
    ) -> AnswerSubmissionResponse:
        """
        Validates session state, patient ownership, question validity, and persists Answer.
        """
        session = db.get(IntakeSession, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Intake session with ID {session_id} not found",
            )

        # Ensure session is in active state or advance from CONSENT_GRANTED
        if session.status == SessionStatus.CONSENT_GRANTED.value:
            session.status = SessionStatus.INTERVIEW_ACTIVE.value
            session.started_at = utcnow()
            db.commit()
            db.refresh(session)
        elif session.status != SessionStatus.INTERVIEW_ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot record answers on session with status '{session.status}'. Expected INTERVIEW_ACTIVE.",
            )

        # Patient ownership check
        patient_id = payload.patient_id or session.patient_id
        if session.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patient ID does not match session patient ID",
            )

        # Validate question if question_id provided
        question: Optional[Question] = None
        if payload.question_id:
            question = db.get(Question, payload.question_id)
            if not question:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Question with ID {payload.question_id} not found",
                )

            # Verify question belongs to active workflow
            workflow = WorkflowService.get_active_workflow(
                db,
                medical_stream_id=session.medical_stream_id,
                department_id=session.department_id,
            )
            if question.workflow_id != workflow.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Question does not belong to session's active clinical workflow '{workflow.name}'",
                )

        now = utcnow()
        answer = Answer(
            id=uuid.uuid4(),
            session_id=session.id,
            question_id=payload.question_id,
            patient_id=session.patient_id,
            raw_answer=payload.raw_answer,
            normalized_answer=payload.normalized_answer,
            answer_type=payload.answer_type.upper(),
            source=payload.source.upper(),
            confidence=payload.confidence,
            answered_at=now,
            is_patient_corrected=payload.is_patient_corrected,
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)

        # Check if more questions are available
        has_next = False
        if session.medical_stream_id:
            try:
                wf = WorkflowService.get_active_workflow(
                    db,
                    medical_stream_id=session.medical_stream_id,
                    department_id=session.department_id,
                )
                stmt_q = select(Question.id).where(Question.workflow_id == wf.id)
                all_q_ids = set(db.scalars(stmt_q).all())

                stmt_a = select(Answer.question_id).where(
                    Answer.session_id == session.id,
                    Answer.question_id.is_not(None),
                )
                ans_ids = set(db.scalars(stmt_a).all())
                has_next = len(all_q_ids - ans_ids) > 0
            except Exception:
                has_next = False

        return AnswerSubmissionResponse(
            answer_id=answer.id,
            saved=True,
            next_question_available=has_next,
            message="Answer recorded successfully",
        )

    @staticmethod
    def get_session_answers(db: Session, session_id: uuid.UUID) -> list[Answer]:
        stmt = (
            select(Answer)
            .where(Answer.session_id == session_id)
            .order_by(Answer.answered_at.asc())
        )
        return list(db.scalars(stmt).all())
