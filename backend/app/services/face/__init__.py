"""Face service exports."""
from app.services.face.base import FaceService
from app.services.face.insightface_service import InsightFaceService


def get_face_service() -> FaceService:
    """Returns the singleton InsightFace biometric recognition service."""
    return InsightFaceService.get_instance()


__all__ = ["FaceService", "InsightFaceService", "get_face_service"]
