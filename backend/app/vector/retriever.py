import hashlib
from typing import Any

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class VectorRetriever:
    def __init__(self) -> None:
        self.model: SentenceTransformer | None = None
        self.collection = settings.qdrant_collection
        self.client: QdrantClient | None = None
        self._local_points: list[dict[str, Any]] = []
        self._embedding_size = 384
        try:
            self.model = SentenceTransformer(settings.embedding_model)
        except Exception:
            # Deterministic local embedding fallback when model download is blocked.
            self.model = None
        try:
            self.client = QdrantClient(url=settings.qdrant_url)
            self._ensure_collection()
        except Exception:
            # Local fallback keeps app functional when Qdrant is unavailable.
            self.client = None

    def _ensure_collection(self) -> None:
        if self.client is None:
            return
        names = [c.name for c in self.client.get_collections().collections]
        if self.collection not in names:
            self.client.create_collection(self.collection, vectors_config=VectorParams(size=384, distance=Distance.COSINE))

    def _embed(self, text: str) -> list[float]:
        if self.model is not None:
            vec = self.model.encode(text)
            return np.array(vec, dtype=np.float32).tolist()
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        raw = np.frombuffer(digest * 24, dtype=np.uint8).astype(np.float32)[: self._embedding_size]
        norm = np.linalg.norm(raw)
        vec = raw / norm if norm else raw
        return vec.tolist()

    async def upsert_chunks(self, chunks: list[dict[str, Any]]) -> None:
        points: list[PointStruct] = []
        for chunk in chunks:
            vector = self._embed(chunk["text"])
            if self.client is None:
                self._local_points.append({**chunk, "_vector": vector})
                continue
            pid = int(hashlib.sha1(chunk["id"].encode("utf-8")).hexdigest()[:12], 16)
            points.append(PointStruct(id=pid, vector=vector, payload=chunk))
        if points and self.client is not None:
            self.client.upsert(collection_name=self.collection, points=points)

    async def retrieve(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        query_vec = np.array(self._embed(query), dtype=np.float32)
        if self.client is None:
            scored: list[tuple[float, dict[str, Any]]] = []
            for point in self._local_points:
                vec = np.array(point["_vector"], dtype=np.float32)
                denom = np.linalg.norm(query_vec) * np.linalg.norm(vec)
                score = float(np.dot(query_vec, vec) / denom) if denom else 0.0
                scored.append((score, point))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [
                {
                    "id": p.get("id", ""),
                    "text": p.get("text", ""),
                    "source": p.get("source", ""),
                    "score": s,
                }
                for s, p in scored[:limit]
            ]

        hits = self.client.query_points(
            collection_name=self.collection,
            query=query_vec.tolist(),
            limit=limit,
            with_payload=True,
        ).points
        return [
            {
                "id": h.payload.get("id", ""),
                "text": h.payload.get("text", ""),
                "source": h.payload.get("source", ""),
                "score": float(h.score),
            }
            for h in hits
        ]
