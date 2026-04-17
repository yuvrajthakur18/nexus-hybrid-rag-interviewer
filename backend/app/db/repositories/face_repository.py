from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import FaceIdentity


class FaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert_identity(self, user_id: str, embedding_vector: list[float], embedding_model: str, enrollment_meta: dict) -> FaceIdentity:
        existing = self.db.scalar(select(FaceIdentity).where(FaceIdentity.user_id == user_id))
        if existing:
            existing.embedding_vector = embedding_vector
            existing.embedding_model = embedding_model
            existing.enrollment_meta = enrollment_meta
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        identity = FaceIdentity(user_id=user_id, embedding_vector=embedding_vector, embedding_model=embedding_model, enrollment_meta=enrollment_meta)
        self.db.add(identity)
        self.db.commit()
        self.db.refresh(identity)
        return identity

    def get_by_user_id(self, user_id: str) -> FaceIdentity | None:
        return self.db.scalar(select(FaceIdentity).where(FaceIdentity.user_id == user_id))
