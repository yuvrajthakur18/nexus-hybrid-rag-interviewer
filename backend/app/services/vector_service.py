import chromadb
from chromadb.config import Settings
import os
from app.core.config import settings as app_settings
from sentence_transformers import SentenceTransformer

class VectorService:
    def __init__(self):
        # Local persistence directory
        persist_directory = os.path.join(os.getcwd(), "data", "chroma_db")
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=app_settings.qdrant_collection or "hybrid_rag_docs"
        )
        self.model = SentenceTransformer(app_settings.embedding_model)

    async def add_documents(self, texts: list[str], metadatas: list[dict], ids: list[str]):
        embeddings = self.model.encode(texts).tolist()
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    async def semantic_search(self, query: str, limit: int = 5):
        query_embedding = self.model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=limit
        )
        
        formatted = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                formatted.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "id": results['ids'][0][i],
                    "score": results['distances'][0][i] if results['distances'] else 0.0
                })
        return formatted, []

    async def upsert_chunks(self, chunks: list[dict]):
        texts = [c["text"] for c in chunks]
        metadatas = [{k: v for k, v in c.items() if k != "text"} for c in chunks]
        ids = [c.get("id") or str(hash(c["text"])) for c in chunks]
        await self.add_documents(texts, metadatas, ids)

vector_service = VectorService()
