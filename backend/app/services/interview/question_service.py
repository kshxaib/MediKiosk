"""Adaptive Questioning Engine foundation service."""
import uuid
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.clinical_workflow import ClinicalWorkflow
from app.models.intake_session import IntakeSession, SessionStatus
from app.models.question import Question
from app.schemas.question import NextQuestionResponse
from app.services.interview.workflow_service import WorkflowService
from app.utils.datetime import utcnow


class QuestionService:
    @staticmethod
    def get_next_question(db: Session, session_id: uuid.UUID) -> NextQuestionResponse:
        """
        Deterministic adaptive foundation for selecting the next unanswered question
        based on session stream, department, language, and previous answers.
        """
        session = db.get(IntakeSession, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Intake session with ID {session_id} not found",
            )

        # Ensure session is active or transition from CONSENT_GRANTED
        if session.status == SessionStatus.CONSENT_GRANTED.value:
            session.status = SessionStatus.INTERVIEW_ACTIVE.value
            session.started_at = utcnow()
            db.commit()
            db.refresh(session)
        elif session.status != SessionStatus.INTERVIEW_ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot retrieve next question for session with status '{session.status}'. Expected INTERVIEW_ACTIVE.",
            )

        if not session.medical_stream_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session does not have a medical stream selected.",
            )

        # 1. Resolve workflow
        workflow = WorkflowService.get_active_workflow(
            db,
            medical_stream_id=session.medical_stream_id,
            department_id=session.department_id,
        )

        # 2. Fetch all workflow questions in session's language
        lang = session.language or "en"
        stmt = (
            select(Question)
            .where(
                Question.workflow_id == workflow.id,
                Question.language == lang,
            )
            .order_by(Question.sequence.asc())
        )
        questions = list(db.scalars(stmt).all())

        # Fallback to 'en' if no questions in specific language
        if not questions and lang != "en":
            stmt_en = (
                select(Question)
                .where(
                    Question.workflow_id == workflow.id,
                    Question.language == "en",
                )
                .order_by(Question.sequence.asc())
            )
            questions = list(db.scalars(stmt_en).all())

        if not questions:
            return NextQuestionResponse(
                completed=True,
                total_questions=0,
                completed_questions=0,
                message=f"No questions configured for workflow '{workflow.name}'",
            )

        # 3. Fetch answered question IDs for this session
        ans_stmt = select(Answer.question_id).where(
            Answer.session_id == session.id,
            Answer.question_id.is_not(None),
        )
        answered_ids = set(db.scalars(ans_stmt).all())

        # 4. Find next unanswered question
        total = len(questions)
        completed_count = sum(1 for q in questions if q.id in answered_ids)

        next_q: Optional[Question] = None
        for q in questions:
            if q.id not in answered_ids:
                next_q = q
                break

        if not next_q:
            return NextQuestionResponse(
                completed=True,
                total_questions=total,
                completed_questions=completed_count,
                is_last_question=True,
                message="All clinical intake questions have been completed.",
            )

        # Generate contextual clinical reason for Phase 5A foundation
        reason = next_q.category.lower() if next_q.category else "clinical_assessment"

        is_last = (completed_count + 1) >= total

        return NextQuestionResponse(
            question_id=str(next_q.id),
            question=next_q.question_text,
            question_type=next_q.question_type.upper(),
            required=next_q.is_required,
            reason=reason,
            category=next_q.category,
            options=next_q.options,
            sequence=next_q.sequence,
            total_questions=total,
            completed_questions=completed_count,
            is_last_question=is_last,
            completed=False,
        )
