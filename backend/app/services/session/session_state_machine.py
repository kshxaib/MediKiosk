"""Session state machine validation rules."""
from fastapi import HTTPException, status
from app.models.intake_session import SessionStatus

VALID_TRANSITIONS: dict[str, set[str]] = {
    SessionStatus.CREATED.value: {
        SessionStatus.IDENTITY_VERIFIED.value,
        SessionStatus.CANCELLED.value,
    },
    SessionStatus.IDENTITY_VERIFIED.value: {
        SessionStatus.CONSENT_GRANTED.value,
        SessionStatus.CANCELLED.value,
    },
    SessionStatus.CONSENT_GRANTED.value: {
        SessionStatus.INTERVIEW_ACTIVE.value,
        SessionStatus.CANCELLED.value,
    },
    SessionStatus.INTERVIEW_ACTIVE.value: {
        SessionStatus.REVIEW_PENDING.value,
        SessionStatus.CANCELLED.value,
    },
    SessionStatus.REVIEW_PENDING.value: {
        SessionStatus.PATIENT_CONFIRMED.value,
        SessionStatus.INTERVIEW_ACTIVE.value,
        SessionStatus.CANCELLED.value,
    },
    SessionStatus.PATIENT_CONFIRMED.value: {
        SessionStatus.SUMMARY_GENERATED.value,
        SessionStatus.CANCELLED.value,
    },
    SessionStatus.SUMMARY_GENERATED.value: {
        SessionStatus.CASE_ROUTED.value,
        SessionStatus.COMPLETED.value,
        SessionStatus.CANCELLED.value,
    },
    SessionStatus.CASE_ROUTED.value: {
        SessionStatus.COMPLETED.value,
        SessionStatus.CANCELLED.value,
    },
    SessionStatus.COMPLETED.value: set(),
    SessionStatus.CANCELLED.value: set(),
}


def validate_transition(current_status: str, target_status: str) -> None:
    """Validate whether transitioning from current_status to target_status is permitted."""
    if current_status == target_status:
        return

    allowed = VALID_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid session status transition from '{current_status}' to '{target_status}'. "
                f"Allowed target states: {sorted(list(allowed)) or 'None (terminal state)'}."
            ),
        )
