from app.schemas.chat import SourceCitation


class PromptBuilder:
    def build_rag_prompt(self, query: str, context_chunks: list[dict]) -> str:
        compact = "\n".join([f"[{i}] {chunk['text'][:300]}" for i, chunk in enumerate(context_chunks, start=1)])
        return f"Question: {query}\nContext:\n{compact}"

    def citations_from_chunks(self, chunks: list[dict]) -> list[SourceCitation]:
        return [
            SourceCitation(
                source=chunk.get("metadata", {}).get("source", "unknown"),
                chunk_id=str(chunk.get("id", "na")),
                score=float(chunk.get("score", 0.0))
            )
            for chunk in chunks
        ]
