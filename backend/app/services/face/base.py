"""Face Biometric Service Abstraction."""
import uuid
from abc import ABC, abstractmethod
from typing import Tuple
from sqlalchemy.orm import Session

from app.models.face_enrollment import FaceEnrollment


class FaceService(ABC):
    """Abstract interface for face detection, enrollment, and verification."""

    @abstractmethod
    def enroll(
        self,
        db: Session,
        patient_id: uuid.UUID,
        image_bytes: bytes,
    ) -> FaceEnrollment:
        """Extracts face embedding and stores/updates face enrollment."""
        pass

    @abstractmethod
    def verify(
        self,
        db: Session,
        patient_id: uuid.UUID,
        image_bytes: bytes,
    ) -> Tuple[bool, str]:
        """
        Verifies live webcam face against the patient's enrolled biometric.
        Returns: (verified: bool, message: str)
        """
        pass
