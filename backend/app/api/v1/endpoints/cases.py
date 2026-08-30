"""Structured AI Case Summary API endpoints (Phase 5C)."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.case import Case, CaseEdit, EditorType
from app.schemas.case import (
    CaseEditCreate,
    CaseEditRead,
    CaseRead,
    CaseSummaryRequest,
)
from app.services.case import CaseSummaryService
from app.utils.datetime import utcnow

router = APIRouter(tags=["Case Summary"])


@router.post(
    "/sessions/{session_id}/ai/summary",
    response_model=CaseRead,
    summary="Generate the structured AI case summary for an intake session",
)
def generate_case_summary(
    session_id: uuid.UUID,
    payload: CaseSummaryRequest | None = None,
    db: Session = Depends(get_db),
) -> CaseRead:
    """
    Assembles the structured case summary from the session's clinical interview,
    vitals and alerts, plus the patient's real historical records (previous
    documents, timeline events and previous consultations).

    The structured `summary` is assembled deterministically by the backend — no
    LLM is involved in producing it, so it cannot contain invented facts. The
    optional `summary_text` is a prose rendering only, and falls back to
    deterministic text whenever the LLM is unavailable or its output fails
    safety validation.

    Current and historical information are kept in separate blocks. No causal
    relationship between them is asserted, and no diagnosis, prescription or
    treatment recommendation is produced.

    Regenerating preserves patient corrections and doctor-verified fields.
    """
    options = payload or CaseSummaryRequest()
    case = CaseSummaryService.generate(
        db, session_id, use_llm_narrative=options.use_llm_narrative
    )
    return CaseRead.model_validate(case)


@router.get(
    "/sessions/{session_id}/ai/summary",
    response_model=CaseRead,
    summary="Fetch the case summary previously generated for a session",
)
def get_case_summary_for_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> CaseRead:
    case = CaseSummaryService.get_case_for_session(db, session_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No case summary has been generated for session {session_id}",
        )
    return CaseRead.model_validate(case)


@router.get(
    "/cases/{case_id}",
    response_model=CaseRead,
    summary="Fetch a case by ID",
)
def get_case(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> CaseRead:
    return CaseRead.model_validate(CaseSummaryService.get_case(db, case_id))


@router.post(
    "/cases/{case_id}/edits",
    response_model=CaseEditRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record a patient or doctor correction to a case summary field",
)
def create_case_edit(
    case_id: uuid.UUID,
    payload: CaseEditCreate,
    db: Session = Depends(get_db),
) -> CaseEditRead:
    """
    Records a correction and immediately re-applies it to the stored summary.

    Patient corrections override the AI draft. Doctor corrections override
    everything and are re-applied on every regeneration, so AI output can never
    silently overwrite doctor-verified information.
    """
    case = CaseSummaryService.get_case(db, case_id)

    editor_type = payload.editor_type.upper()
    if editor_type not in {e.value for e in EditorType}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid editor_type '{payload.editor_type}'. "
                f"Expected one of {sorted(e.value for e in EditorType)}."
            ),
        )

    summary = case.summary or {}
    node: object = summary
    for part in payload.field_name.split("."):
        if not isinstance(node, dict) or part not in node:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unknown summary field '{payload.field_name}'. A correction "
                    f"may only target a field that already exists in the summary."
                ),
            )
        node = node[part]
    old_value = node.get("value") if isinstance(node, dict) and "value" in node else node

    edit = CaseEdit(
        id=uuid.uuid4(),
        case_id=case.id,
        edited_by=payload.edited_by,
        editor_type=editor_type,
        field_name=payload.field_name,
        old_value={"value": old_value},
        new_value={"value": payload.new_value},
        reason=payload.reason,
        created_at=utcnow(),
    )
    db.add(edit)
    db.commit()
    db.refresh(edit)

    # Re-apply corrections onto the stored summary without re-running the LLM.
    CaseSummaryService.generate(db, case.session_id, use_llm_narrative=False)
    db.refresh(edit)
    return CaseEditRead.model_validate(edit)


@router.get(
    "/cases/{case_id}/edits",
    response_model=list[CaseEditRead],
    summary="List all corrections recorded against a case",
)
def list_case_edits(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[CaseEditRead]:
    CaseSummaryService.get_case(db, case_id)
    edits = list(
        db.scalars(
            select(CaseEdit)
            .where(CaseEdit.case_id == case_id)
            .order_by(CaseEdit.created_at.asc())
        ).all()
    )
    return [CaseEditRead.model_validate(e) for e in edits]
