from pydantic import BaseModel, Field


class EnrollFaceRequest(BaseModel):
    user_id: str
    image_sequence_base64: list[str] = Field(..., min_length=2)


class VerifyFaceRequest(BaseModel):
    user_id: str
    image_sequence_base64: list[str] = Field(..., min_length=2)
    challenge_response: str | None = None


class AuthResponse(BaseModel):
    success: bool
    token: str | None = None
    message: str
