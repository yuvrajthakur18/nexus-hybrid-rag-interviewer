from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import ChatMessage, ChatSession


class ChatRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_session(self, user_id: str) -> ChatSession:
        session = ChatSession(user_id=user_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def add_message(self, session_id: int, role: str, content: str) -> ChatMessage:
        msg = ChatMessage(session_id=session_id, role=role, content=content)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_session(self, session_id: int) -> ChatSession | None:
        stmt = select(ChatSession).options(selectinload(ChatSession.messages)).where(ChatSession.id == session_id)
        return self.db.scalar(stmt)
