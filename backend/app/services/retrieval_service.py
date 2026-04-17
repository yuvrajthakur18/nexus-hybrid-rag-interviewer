from time import perf_counter
from app.services.vector_service import vector_service


class RetrievalService:
    async def semantic_search(self, query: str, limit: int = 5) -> tuple[list[dict], float]:
        started = perf_counter()
        chunks, _ = await vector_service.semantic_search(query, limit=limit)
        return chunks, (perf_counter() - started) * 1000
