"""Identity & Biometric schemas."""
import uuid
from pydantic import BaseModel, Field


class FaceEnrollRequest(BaseModel):
    """Payload for face enrollment from webcam."""
    patient_id: uuid.UUID
    image_base64: str = Field(..., min_length=20, description="Base64 encoded webcam image (JPEG/PNG)")


class FaceEnrollResponse(BaseModel):
    """Response after enrolling face biometric."""
    patient_id: uuid.UUID
    enrollment_status: str = "success"
    message: str = "Face biometric enrolled successfully"


class FaceVerifyRequest(BaseModel):
    """Payload for face verification against stored enrollment."""
    patient_id: uuid.UUID
    image_base64: str = Field(..., min_length=20, description="Base64 encoded live webcam image")


class FaceVerifyResponse(BaseModel):
    """Response returned after live face verification."""
    verified: bool
    patient_id: uuid.UUID
    method: str = "face_arcface"
    message: str
