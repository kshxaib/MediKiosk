"""InsightFace ArcFace Biometric Service implementation."""
import base64
import json
import uuid
from typing import Optional, Tuple
import cv2
import numpy as np
from fastapi import HTTPException, status
import insightface
from insightface.app import FaceAnalysis
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.face_enrollment import FaceEnrollment
from app.models.patient import Patient
from app.services.face.base import FaceService
from app.utils.datetime import utcnow


class InsightFaceService(FaceService):
    """
    Production-grade biometric facial recognition service using
    InsightFace ArcFace (buffalo_l: SCRFD face detection + w600k_r50 recognition).
    """

    _instance: Optional["InsightFaceService"] = None

    def __init__(self) -> None:
        self.app = FaceAnalysis(
            name=settings.FACE_MODEL_NAME,
            providers=["CPUExecutionProvider"],
        )
        self.app.prepare(
            ctx_id=0,
            det_size=(settings.FACE_DETECTION_SIZE, settings.FACE_DETECTION_SIZE),
        )
        self.threshold = settings.FACE_SIMILARITY_THRESHOLD

    @classmethod
    def get_instance(cls) -> "InsightFaceService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _decode_image(self, image_bytes: bytes) -> np.ndarray:
        """Decode raw image bytes to BGR numpy array."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image format. Could not decode image.",
            )
        return img

    def _extract_embedding(self, image_bytes: bytes) -> np.ndarray:
        """Detect face and extract normalized 512-d ArcFace embedding vector."""
        img = self._decode_image(image_bytes)
        faces = self.app.get(img)

        if not faces or len(faces) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No face detected in capture. Please look directly into the camera with good lighting.",
            )

        # Select the largest face by bounding box area
        best_face = max(
            faces,
            key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]),
        )
        embedding = best_face.normed_embedding
        return embedding

    def enroll(
        self,
        db: Session,
        patient_id: uuid.UUID,
        image_bytes: bytes,
    ) -> FaceEnrollment:
        """Extract biometric embedding and persist active FaceEnrollment."""
        patient = db.get(Patient, patient_id)
        if not patient or not patient.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found or inactive",
            )

        embedding = self._extract_embedding(image_bytes)
        embedding_json = json.dumps(embedding.tolist())

        # Revoke existing active enrollments for this patient
        stmt = select(FaceEnrollment).where(
            FaceEnrollment.patient_id == patient_id,
            FaceEnrollment.status == "ACTIVE",
        )
        for existing in db.scalars(stmt).all():
            existing.status = "REVOKED"
            existing.updated_at = utcnow()
            db.add(existing)

        enrollment = FaceEnrollment(
            patient_id=patient_id,
            embedding_reference=embedding_json,
            model_name=f"insightface_{settings.FACE_MODEL_NAME}_arcface",
            model_version="1.0.1",
            status="ACTIVE",
            enrolled_at=utcnow(),
            updated_at=utcnow(),
        )
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment

    def verify(
        self,
        db: Session,
        patient_id: uuid.UUID,
        image_bytes: bytes,
    ) -> Tuple[bool, str]:
        """
        Verify live captured face against stored active enrollment using cosine similarity.
        """
        patient = db.get(Patient, patient_id)
        if not patient or not patient.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found or inactive",
            )

        stmt = select(FaceEnrollment).where(
            FaceEnrollment.patient_id == patient_id,
            FaceEnrollment.status == "ACTIVE",
        ).order_by(FaceEnrollment.enrolled_at.desc())
        enrollment = db.scalars(stmt).first()

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active face biometric enrollment found for this patient. Please enroll first.",
            )

        live_embedding = self._extract_embedding(image_bytes)
        stored_embedding = np.array(json.loads(enrollment.embedding_reference), dtype=np.float32)

        # Calculate cosine similarity: dot product of normalized vectors
        similarity = float(np.dot(live_embedding, stored_embedding))

        if similarity >= self.threshold:
            return True, "Identity verified successfully"
        else:
            return False, "Face verification failed. Biometric match score below threshold."
