from fastapi.testclient import TestClient
import pytest
from unittest.mock import AsyncMock

from app.main import app
from app.services.face_auth_service import FaceAuthService
from app.orchestration.hybrid_orchestrator import HybridOrchestrator

client = TestClient(app)

def test_chat_lifecycle_with_jwt_protection(monkeypatch) -> None:
    # 1. Mock FaceAuthService
    import numpy as np

    def fake_to_face_embedding_and_kps(self, image_bytes: bytes):
        emb = np.ones(512, dtype=np.float32)
        emb = emb / np.linalg.norm(emb)
        call_idx = getattr(self, "_test_call_idx", 0)
        setattr(self, "_test_call_idx", call_idx + 1)
        if call_idx < 2:
            kps = np.array([[0.0, 10.0], [1.0, 10.0], [0.0, 0.0]], dtype=np.float32)
        else:
            kps = np.array([[0.0, 10.0], [1.0, 10.0], [0.0, 20.0]], dtype=np.float32)
        return emb, kps

    monkeypatch.setattr(FaceAuthService, "_to_face_embedding_and_kps", fake_to_face_embedding_and_kps)

    # 2. Mock Hybrid Orchestrator
    async def mock_run(self, query):
        return {
            "answer": "Hello, I am a mock assistant.",
            "strategy": "mock_strategy",
            "citations": [],
            "latency_ms": 10
        }
    monkeypatch.setattr(HybridOrchestrator, "run", mock_run)

    user_id = "test-user-auth"
    mock_sequence = ["aGVsbG8="] * 5

    # Access without auth
    resp = client.post("/chat/query", json={"user_id": user_id, "query": "hello"})
    assert resp.status_code in (401, 403)

    # Enroll
    enroll_resp = client.post("/auth/enroll-face", json={
        "user_id": user_id,
        "image_sequence_base64": mock_sequence
    })
    assert enroll_resp.status_code == 200
    assert enroll_resp.json()["success"] is True

    # Reset _test_call_idx on the FaceAuthService class via a fake instance if needed
    # (FastAPI will create a new instance, so the getattr would return 0 anyway because we attach to `self`, but wait, we attached to `self`, not `FaceAuthService`, so a new instance starts at 0. Perfect.)
    
    # Verify
    verify_resp = client.post("/auth/verify-face", json={
        "user_id": user_id,
        "image_sequence_base64": mock_sequence,
        "challenge_response": "blink"
    })
    
    assert verify_resp.status_code == 200
    assert verify_resp.json()["success"] is True
    token = verify_resp.json()["token"]

    # Access with invalid user
    resp_wrong_user = client.post("/chat/query", json={"user_id": "other-user", "query": "hello"}, headers={"Authorization": f"Bearer {token}"})
    assert resp_wrong_user.status_code == 403

    # Access with auth
    resp_ok = client.post("/chat/query", json={"user_id": user_id, "query": "hello"}, headers={"Authorization": f"Bearer {token}"})
    assert resp_ok.status_code == 200
    data = resp_ok.json()
    assert data["answer"] == "Hello, I am a mock assistant."
    assert "session_id" in data

