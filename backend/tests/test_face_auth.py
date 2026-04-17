from app.services.face_auth_service import FaceAuthService


def test_face_auth_pass(monkeypatch) -> None:
    svc = FaceAuthService()
    import numpy as np

    def fake_to_face_embedding_and_kps(self, image_bytes: bytes):
        # Deterministic embedding + keypoints that satisfy blink challenge.
        emb = np.ones(512, dtype=np.float32)
        emb = emb / np.linalg.norm(emb)

        # Return different keypoints depending on call order:
        # first half -> higher metric, second half -> lower metric (blink).
        # This ensures start/end averages differ.
        call_idx = getattr(self, "_test_call_idx", 0)
        setattr(self, "_test_call_idx", call_idx + 1)
        if call_idx < 2:
            kps = np.array([[0.0, 10.0], [1.0, 10.0], [0.0, 0.0]], dtype=np.float32)
        else:
            kps = np.array([[0.0, 10.0], [1.0, 10.0], [0.0, 20.0]], dtype=np.float32)
        return emb, kps

    monkeypatch.setattr(FaceAuthService, "_to_face_embedding_and_kps", fake_to_face_embedding_and_kps)

    user_id = "user-1"
    seq = ["aGVsbG8=", "d29ybGQ=", "aGVsbG8=", "d29ybGQ="]  # 4 frames for blink windowing

    template, _meta = svc.enroll_sequence(user_id, seq)
    # Reset call counter so verify_sequence uses the intended keypoint pattern.
    setattr(svc, "_test_call_idx", 0)
    out = svc.verify_sequence(user_id=user_id, image_sequence_base64=seq, enrolled_vector=template, challenge_response="blink")
    assert out.success is True
