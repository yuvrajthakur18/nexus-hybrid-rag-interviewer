from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hybrid RAG Interviewer"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    jwt_secret: str = "change-me"
    jwt_expire_minutes: int = 120
    database_url: str = "sqlite:///./hybrid_rag.db"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "hybrid_rag_docs"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_provider: str = "google"
    llm_model: str = "gemini-3.1-flash-lite"
    llm_api_key: str = ""
    face_similarity_threshold: float = 0.78
    enable_image_persistence: bool = False
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
