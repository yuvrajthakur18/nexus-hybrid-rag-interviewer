from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.repositories.chat_repository import ChatRepository
from app.db.session import get_db
from app.orchestration.hybrid_orchestrator import HybridOrchestrator
from app.core.security import verify_access_token
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse

router = APIRouter()
bearer_scheme = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    try:
        return verify_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/query", response_model=ChatQueryResponse)
async def chat_query(
    payload: ChatQueryRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> ChatQueryResponse:
    chats = ChatRepository(db)
    if payload.user_id != user_id:
        raise HTTPException(status_code=403, detail="user_id does not match token")

    sid = payload.session_id or chats.create_session(user_id).id
    result = await HybridOrchestrator(db).run(payload.query)
    chats.add_message(sid, "user", payload.query)
    chats.add_message(sid, "assistant", result["answer"])
    return ChatQueryResponse(session_id=sid, answer=result["answer"], strategy=result["strategy"], citations=result["citations"], latency_ms=result["latency_ms"])


from fastapi.responses import StreamingResponse
import json

@router.post("/query-stream")
async def chat_query_stream(
    payload: ChatQueryRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    chats = ChatRepository(db)
    if payload.user_id != user_id:
        raise HTTPException(status_code=403, detail="user_id does not match token")

    sid = payload.session_id or chats.create_session(user_id).id
    chats.add_message(sid, "user", payload.query)
    
    orchestrator = HybridOrchestrator(db)
    
    async def stream_generator():
        full_answer = ""
        async for chunk in orchestrator.run_stream(payload.query):
            # Include session_id in all chunks for frontend state
            chunk["session_id"] = sid
            
            if chunk.get("type") == "content":
                full_answer += chunk.get("answer", "")
            
            yield f"data: {json.dumps(chunk)}\n\n"
        
        # After stream ends, record the full message
        if full_answer:
            chats.add_message(sid, "assistant", full_answer)

    return StreamingResponse(stream_generator(), media_type="text/event-stream")


@router.get("/session/{session_id}")
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    session = ChatRepository(db).get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized for this session")
    return {"session_id": session.id, "user_id": session.user_id, "messages": [{"role": m.role, "content": m.content} for m in session.messages]}
