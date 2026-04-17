from dataclasses import dataclass


@dataclass
class TextChunk:
    id: str
    text: str
    source: str


class Chunker:
    def __init__(self, chunk_size: int = 700, overlap: int = 120) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, source: str) -> list[TextChunk]:
        if not text.strip():
            return []
        chunks: list[TextChunk] = []
        start = 0
        i = 0
        while start < len(text):
            end = min(len(text), start + self.chunk_size)
            chunks.append(TextChunk(id=f"{source}-{i}", text=text[start:end], source=source))
            i += 1
            if end == len(text):
                break
            start = max(0, end - self.overlap)
        return chunks
