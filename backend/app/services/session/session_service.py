"""IntakeSession lifecycle and consent orchestration service."""
import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.consent import Consent
from app.models.department import Department
from app.models.hospital import Hospital
from app.models.intake_session import IntakeSession, SessionStatus
from app.models.medical_stream import MedicalStream
from app.models.patient import Patient
from app.schemas.session import ConsentCreate, SessionCreate, SessionUpdate
from app.services.session.session_state_machine import validate_transition
from app.utils.datetime import utcnow


class SessionService:
    """Encapsulates all session state management, consent recording, and validation."""

    @staticmethod
    def create_session(db: Session, payload: SessionCreate) -> IntakeSession:
        # 1. Verify patient exists and is active
        patient = db.get(Patient, payload.patient_id)
        if not patient or not patient.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active patient with ID {payload.patient_id} not found",
            )

        # 2. Verify hospital
        hospital_id = payload.hospital_id
        if hospital_id:
            hospital = db.get(Hospital, hospital_id)
            if not hospital or not hospital.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Active hospital with ID {hospital_id} not found",
                )
        else:
            # Fallback to default active hospital
            stmt = select(Hospital).where(Hospital.is_active.is_(True)).order_by(Hospital.created_at)
            hospital = db.scalars(stmt).first()
            if not hospital:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No active hospital configured in database",
                )
            hospital_id = hospital.id

        # 3. Verify medical stream if provided
        if payload.medical_stream_id:
            stream = db.get(MedicalStream, payload.medical_stream_id)
            if not stream or not stream.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Active medical stream with ID {payload.medical_stream_id} not found",
                )

        # 4. Verify department if provided
        if payload.department_id:
            dept = db.get(Department, payload.department_id)
            if not dept or not dept.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Active department with ID {payload.department_id} not found",
                )
            if dept.hospital_id != hospital_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Department {dept.name} does not belong to hospital {hospital.name}",
                )

        # Check if patient already has biometric verification completed (or start as IDENTITY_VERIFIED)
        # Default starting state for verified patient is IDENTITY_VERIFIED
        session = IntakeSession(
            id=uuid.uuid4(),
            patient_id=patient.id,
            hospital_id=hospital_id,
            medical_stream_id=payload.medical_stream_id,
            department_id=payload.department_id,
            language=payload.language,
            status=SessionStatus.IDENTITY_VERIFIED.value,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(db: Session, session_id: uuid.UUID) -> IntakeSession:
        session = db.get(IntakeSession, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Intake session with ID {session_id} not found",
            )
        return session

    @staticmethod
    def update_session(
        db: Session,
        session_id: uuid.UUID,
        payload: SessionUpdate,
        patient_id: Optional[uuid.UUID] = None,
    ) -> IntakeSession:
        session = SessionService.get_session(db, session_id)

        # Ownership security check
        if patient_id and session.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Session patient mismatch: unauthorized modification",
            )

        # Validate status change if requested
        if payload.status:
            validate_transition(session.status, payload.status)
            session.status = payload.status

        # Validate medical stream
        if payload.medical_stream_id:
            stream = db.get(MedicalStream, payload.medical_stream_id)
            if not stream or not stream.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Active medical stream with ID {payload.medical_stream_id} not found",
                )
            session.medical_stream_id = payload.medical_stream_id

        # Validate department
        if payload.department_id:
            dept = db.get(Department, payload.department_id)
            if not dept or not dept.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Active department with ID {payload.department_id} not found",
                )
            if dept.hospital_id != session.hospital_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department does not belong to session's hospital",
                )
            session.department_id = payload.department_id

        if payload.language:
            session.language = payload.language

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def record_consent(
        db: Session,
        session_id: uuid.UUID,
        payload: ConsentCreate,
    ) -> Consent:
        session = SessionService.get_session(db, session_id)

        # Security ownership check
        if session.patient_id != payload.patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Consent patient ID does not match session patient ID",
            )

        # Session status check
        if session.status in {SessionStatus.COMPLETED.value, SessionStatus.CANCELLED.value}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot record consent on session in terminal state '{session.status}'",
            )

        now = utcnow()
        consent = Consent(
            id=uuid.uuid4(),
            session_id=session.id,
            patient_id=session.patient_id,
            consent_type=payload.consent_type,
            consent_text=payload.consent_text,
            language=payload.language,
            is_granted=payload.is_granted,
            consented_at=now if payload.is_granted else None,
            withdrawn_at=now if not payload.is_granted else None,
        )
        db.add(consent)

        # State transition on consent result
        if payload.is_granted:
            # Advance to CONSENT_GRANTED if in IDENTITY_VERIFIED or CREATED
            if session.status in {SessionStatus.CREATED.value, SessionStatus.IDENTITY_VERIFIED.value}:
                session.status = SessionStatus.CONSENT_GRANTED.value
        else:
            # When consent is explicitly declined, cancel session
            session.status = SessionStatus.CANCELLED.value

        db.commit()
        db.refresh(consent)
        return consent

    @staticmethod
    def get_consents(db: Session, session_id: uuid.UUID) -> list[Consent]:
        session = SessionService.get_session(db, session_id)
        stmt = select(Consent).where(Consent.session_id == session.id).order_by(Consent.created_at.desc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def start_session(db: Session, session_id: uuid.UUID) -> IntakeSession:
        session = SessionService.get_session(db, session_id)

        if not session.medical_stream_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot start session: Medical stream has not been selected",
            )
        if not session.department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot start session: Department has not been selected",
            )

        validate_transition(session.status, SessionStatus.INTERVIEW_ACTIVE.value)
        session.status = SessionStatus.INTERVIEW_ACTIVE.value
        session.started_at = utcnow()

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def complete_session(db: Session, session_id: uuid.UUID) -> IntakeSession:
        session = SessionService.get_session(db, session_id)
        validate_transition(session.status, SessionStatus.COMPLETED.value)
        session.status = SessionStatus.COMPLETED.value
        session.completed_at = utcnow()

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def clear_session(db: Session, session_id: uuid.UUID) -> IntakeSession:
        session = SessionService.get_session(db, session_id)
        validate_transition(session.status, SessionStatus.CANCELLED.value)
        session.status = SessionStatus.CANCELLED.value

        db.commit()
        db.refresh(session)
        return session
