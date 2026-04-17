from dataclasses import asdict

from pypdf import PdfReader

from app.vector.chunking import Chunker


class VectorIndexer:
    def __init__(self, retriever) -> None:
        self.retriever = retriever
        self.chunker = Chunker()

    def read_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    async def index_pdf(self, file_path: str, doc_id: str) -> int:
        text = self.read_pdf(file_path)
        chunks = self.chunker.chunk_text(text, source=doc_id)
        await self.retriever.upsert_chunks([asdict(c) for c in chunks])
        return len(chunks)
