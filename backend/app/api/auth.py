from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.repositories.face_repository import FaceRepository
from app.db.session import get_db
from app.schemas.auth import AuthResponse, EnrollFaceRequest, VerifyFaceRequest
from app.services.face_auth_service import FaceAuthService

router = APIRouter()


@router.post("/enroll-face", response_model=AuthResponse)
def enroll_face(payload: EnrollFaceRequest, db: Session = Depends(get_db)) -> AuthResponse:
    service = FaceAuthService()
    try:
        emb, meta = service.enroll_sequence(payload.user_id, payload.image_sequence_base64)
    except ValueError as exc:
        msg = str(exc)
        if "no_face_detected" in msg:
            msg = "No face detected in frame. Please ensure you are looking clearly at the camera with good lighting."
        raise HTTPException(status_code=400, detail=msg) from exc
    FaceRepository(db).upsert_identity(payload.user_id, emb, service.model_name, meta)
    return AuthResponse(success=True, message="Face enrollment complete")


@router.post("/verify-face", response_model=AuthResponse)
def verify_face(payload: VerifyFaceRequest, db: Session = Depends(get_db)) -> AuthResponse:
    identity = FaceRepository(db).get_by_user_id(payload.user_id)
    if not identity:
        raise HTTPException(
            status_code=400,
            detail="Identity not enrolled. Please call /auth/enroll-face first for this user_id.",
        )
    service = FaceAuthService()
    try:
        result = service.verify_sequence(
            user_id=payload.user_id,
            image_sequence_base64=payload.image_sequence_base64,
            enrolled_vector=identity.embedding_vector,
            challenge_response=payload.challenge_response,
        )
    except ValueError as exc:
        msg = str(exc)
        if "no_face_detected" in msg:
            msg = "No face detected in frame. Please ensure you are looking clearly at the camera with good lighting."
        raise HTTPException(status_code=400, detail=msg) from exc
    if not result.success:
        detail = f"Auth failed: {result.reason}"
        if "below_threshold" in result.reason:
            detail = "Identity mismatch. Face does not match the enrolled user."
        raise HTTPException(status_code=401, detail=detail)
    token = create_access_token(payload.user_id, claims={"auth_method": "face"})
    return AuthResponse(success=True, token=token, message="Authenticated")
