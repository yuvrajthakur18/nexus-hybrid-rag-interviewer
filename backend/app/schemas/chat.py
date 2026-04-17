from pydantic import BaseModel


class ChatQueryRequest(BaseModel):
    user_id: str
    session_id: int | None = None
    query: str


class SourceCitation(BaseModel):
    source: str
    chunk_id: str
    score: float


class ChatQueryResponse(BaseModel):
    session_id: int
    answer: str
    strategy: str
    citations: list[SourceCitation] = []
    latency_ms: float
