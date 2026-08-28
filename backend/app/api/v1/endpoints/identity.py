"""Patient Biometric Identity API Endpoints."""
import base64
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.identity import (
    FaceEnrollRequest,
    FaceEnrollResponse,
    FaceVerifyRequest,
    FaceVerifyResponse,
)
from app.services.face import get_face_service
from app.services.face.base import FaceService

router = APIRouter(prefix="/identity", tags=["Identity"])


def _extract_image_bytes(base64_str: str) -> bytes:
    """Extract raw image bytes from data URI or raw base64 string."""
    try:
        if "," in base64_str:
            base64_str = base64_str.split(",", 1)[1]
        return base64.b64decode(base64_str)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid base64 image data: {str(e)}",
        )


@router.post(
    "/face/enroll",
    response_model=FaceEnrollResponse,
    summary="Enroll patient face biometric",
)
def enroll_face(
    payload: FaceEnrollRequest,
    db: Session = Depends(get_db),
    face_service: FaceService = Depends(get_face_service),
) -> FaceEnrollResponse:
    """
    Extracts face embedding from webcam capture and stores active FaceEnrollment.
    """
    image_bytes = _extract_image_bytes(payload.image_base64)
    face_service.enroll(db, payload.patient_id, image_bytes)
    return FaceEnrollResponse(
        patient_id=payload.patient_id,
        enrollment_status="success",
        message="Face biometric enrolled successfully",
    )


@router.post(
    "/face/verify",
    response_model=FaceVerifyResponse,
    summary="Verify live webcam face biometric",
)
def verify_face(
    payload: FaceVerifyRequest,
    db: Session = Depends(get_db),
    face_service: FaceService = Depends(get_face_service),
) -> FaceVerifyResponse:
    """
    Compares live webcam capture with enrolled biometric.
    Returns verified=True on biometric match, verified=False on mismatch.
    """
    image_bytes = _extract_image_bytes(payload.image_base64)
    verified, message = face_service.verify(db, payload.patient_id, image_bytes)
    return FaceVerifyResponse(
        verified=verified,
        patient_id=payload.patient_id,
        method="face_arcface",
        message=message,
    )
