from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class DesignerProfile(Base):
    __tablename__ = "designer_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=False)
    specialization: Mapped[str] = mapped_column(String(120), nullable=False)
    strengths: Mapped[dict] = mapped_column(JSON, default=dict)


class GameGenre(Base):
    __tablename__ = "game_genres"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")


class CharacterArchetype(Base):
    __tablename__ = "character_archetypes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    design_notes: Mapped[str] = mapped_column(Text, default="")


class SkillTree(Base):
    __tablename__ = "skill_trees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    archetype_id: Mapped[int] = mapped_column(ForeignKey("character_archetypes.id"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    nodes: Mapped[dict] = mapped_column(JSON, default=dict)


class StatSystem(Base):
    __tablename__ = "stat_systems"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    system_name: Mapped[str] = mapped_column(String(120), nullable=False)
    primary_stats: Mapped[dict] = mapped_column(JSON, default=dict)


class ProductionConstraint(Base):
    __tablename__ = "production_constraints"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_name: Mapped[str] = mapped_column(String(120), nullable=False)
    platform: Mapped[str] = mapped_column(String(60), nullable=False)
    memory_budget_mb: Mapped[int] = mapped_column(Integer, nullable=False)
    timeline_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    max_asset_polycount: Mapped[int] = mapped_column(Integer, nullable=False)


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(40), nullable=False)
    expected_competency: Mapped[str] = mapped_column(String(120), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)


class FaceIdentity(Base):
    __tablename__ = "face_identities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    embedding_vector: Mapped[list[float]] = mapped_column(JSON, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(120), nullable=False)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    enrollment_meta: Mapped[dict] = mapped_column(JSON, default=dict)


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    session: Mapped[ChatSession] = relationship(back_populates="messages")


class RetrievalTrace(Base):
    __tablename__ = "retrieval_traces"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    trace_meta: Mapped[dict] = mapped_column(JSON, default=dict)
