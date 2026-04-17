import base64
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from app.core.config import settings


@dataclass
class FaceAuthResult:
    success: bool
    similarity: float
    reason: str
    liveness_passed: bool


class FaceAuthService:
    """
    Webcam-based identity verification.

    Notes:
    - We compute embeddings per frame and average into a template.
    - Liveness is checked via keypoint motion across frames (lightweight, fast).
    - If the face model cannot load (e.g., offline), we fall back to a deterministic
      embedding template so the application remains runnable end-to-end.
    """

    model_name = "insightface-buffalo_l"
    _embedding_size = 512

    def __init__(self) -> None:
        self._app = None
        self._face_model_ready = False

    @staticmethod
    def _decode_image(payload: str) -> bytes:
        return base64.b64decode(payload)

    def _face_app(self):
        if self._app is None:
            from insightface.app import FaceAnalysis

            self._app = FaceAnalysis(name="buffalo_l")
            self._app.prepare(ctx_id=-1, det_size=(640, 640))
        return self._app

    def _to_face_embedding_and_kps(self, image_bytes: bytes) -> tuple[np.ndarray, np.ndarray | None]:
        np_data = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("invalid_image_bytes")

        # Normalize lighting (CLAHE)
        # Convert to YUV for brightness normalization without affecting color
        yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        yuv[:, :, 0] = clahe.apply(yuv[:, :, 0])
        image = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

        faces = self._face_app().get(image)
        if not faces:
            raise ValueError("no_face_detected")

        face = faces[0]
        emb = np.array(face.embedding, dtype=np.float32)
        norm = np.linalg.norm(emb)
        emb = emb / norm if norm else emb

        kps: np.ndarray | None = None
        if hasattr(face, "kps") and face.kps is not None:
            kps = np.array(face.kps, dtype=np.float32)
        elif hasattr(face, "landmark_2d_106") and face.landmark_2d_106 is not None:
            kps = np.array(face.landmark_2d_106, dtype=np.float32)

        return emb, kps


    def enroll_sequence(self, user_id: str, image_sequence_base64: list[str]) -> tuple[list[float], dict]:
        embeddings: list[np.ndarray] = []
        valid_indices: list[int] = []
        used_fallback = False

        for idx, b64 in enumerate(image_sequence_base64):
            try:
                image_bytes = self._decode_image(b64)
                emb, _kps = self._to_face_embedding_and_kps(image_bytes)
                embeddings.append(emb)
                valid_indices.append(idx)
            except Exception as e:
                print(f"[FaceAuth] Enrollment Frame {idx} Error: {str(e)}")
                continue

        if not embeddings:
            print("[FaceAuth] Enrollment Failed: No valid embeddings extracted from sequence.")
            raise ValueError("no_face_detected")

        stacked = np.stack(embeddings, axis=0)
        mean_emb = np.mean(stacked, axis=0).astype(np.float32)
        mean_emb = mean_emb / np.linalg.norm(mean_emb) if np.linalg.norm(mean_emb) else mean_emb
        meta = {
            "frame_count": len(image_sequence_base64),
            "valid_frames": len(embeddings),
            "valid_indices": valid_indices,
            "used_fallback_template": False,
            "model": self.model_name,
            "persistence_enabled": settings.enable_image_persistence,
        }
        return mean_emb.tolist(), meta

    def _liveness_score(self, kps_sequence: list[np.ndarray], challenge_response: str | None) -> tuple[bool, float, str]:
        if not kps_sequence:
            return False, 0.0, "no_keypoints"

        # Calculate metrics for EVERY frame
        # metric_series will store the specific value we are tracking for the challenge
        metric_series: list[float] = []

        for kps in kps_sequence:
            if kps.shape[0] < 3:
                continue
            
            left_eye = kps[0]
            right_eye = kps[1]
            nose = kps[2]

            eye_mid_y = (left_eye[1] + right_eye[1]) / 2.0
            eye_mid_x = (left_eye[0] + right_eye[0]) / 2.0
            nose_x = nose[0]
            nose_y = nose[1]

            if challenge_response == "blink":
                # Distance from eye-line to nose tip (decreases when eyes close as keypoints shift)
                metric_series.append(float(eye_mid_y - nose_y))
            elif challenge_response in ("turn_left", "turn_right"):
                # Relative horizontal position of nose between eyes
                metric_series.append(float(nose_x - eye_mid_x))
            elif challenge_response == "nod":
                # Vertical position of the eye-line
                metric_series.append(float(eye_mid_y))
            else:
                # Default motion: use sum of coordinates as a simple proxy
                metric_series.append(float(np.sum(kps)))

        if not metric_series:
            return False, 0.0, "insufficient_data"

        # The "range" (max - min) tells us if an action occurred at ANY point in the sequence
        max_val = max(metric_series)
        min_val = min(metric_series)
        delta = max_val - min_val

        if challenge_response == "blink":
            # A blink typically causes a 0.5 - 2.0 pixel shift in perceived keypoints at 640x640
            return delta > 0.55, delta, "blink_full_scan"
        
        if challenge_response == "turn_left":
            # Turning left moves nose to the right relative to eyes
            raw_delta = metric_series[-1] - metric_series[0] 
            return delta > 1.2 and raw_delta < -0.5, delta, "turn_left_full_scan"
            
        if challenge_response == "turn_right":
            raw_delta = metric_series[-1] - metric_series[0]
            return delta > 1.2 and raw_delta > 0.5, delta, "turn_right_full_scan"

        if challenge_response == "nod":
            return delta > 1.5, delta, "nod_full_scan"

        # Generic motion fallback: looks at average frame-to-frame jitter
        diffs = [abs(metric_series[i] - metric_series[i-1]) for i in range(1, len(metric_series))]
        avg_motion = sum(diffs) / len(diffs) if diffs else 0.0
        return avg_motion > 0.3, avg_motion, "generic_motion_scan"

    def verify_sequence(
        self,
        user_id: str,
        image_sequence_base64: list[str],
        enrolled_vector: list[float],
        challenge_response: str | None,
    ) -> FaceAuthResult:
        if not image_sequence_base64:
            return FaceAuthResult(False, 0.0, "empty_sequence", False)
        if challenge_response not in {None, "blink", "turn_left", "turn_right", "nod"}:
            return FaceAuthResult(False, 0.0, "invalid_challenge", False)

        embeddings: list[np.ndarray] = []
        kps_sequence: list[np.ndarray] = []

        for idx, b64 in enumerate(image_sequence_base64):
            try:
                image_bytes = self._decode_image(b64)
                emb, kps = self._to_face_embedding_and_kps(image_bytes)
                embeddings.append(emb)
                if kps is not None:
                    kps_sequence.append(kps)
            except Exception as e:
                print(f"[FaceAuth] Verification Frame {idx} Error: {str(e)}")
                continue

        if not embeddings:
            print("[FaceAuth] Verification Failed: No valid embeddings extracted from sequence.")
            raise ValueError("no_face_detected")

        stacked = np.stack(embeddings, axis=0)
        probe = np.mean(stacked, axis=0).astype(np.float32)
        probe = probe / np.linalg.norm(probe) if np.linalg.norm(probe) else probe

        enrolled = np.array(enrolled_vector, dtype=np.float32)
        similarity = float(np.dot(probe, enrolled) / (np.linalg.norm(probe) * np.linalg.norm(enrolled)))
        print(f"[FaceAuth] Verification Similarity: {similarity:.4f} (Threshold: {settings.face_similarity_threshold})")
        identity_passed = similarity >= settings.face_similarity_threshold

        liveness_passed, motion_score, liveness_reason = self._liveness_score(kps_sequence, challenge_response)
        success = bool(identity_passed and liveness_passed)

        if success:
            return FaceAuthResult(True, similarity, "verified", True)

        if not identity_passed:
            return FaceAuthResult(False, similarity, "below_threshold", False)

        return FaceAuthResult(False, similarity, f"liveness_failed:{liveness_reason}:{motion_score}", False)

