import os
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.ingest import IngestResponse
from app.vector.indexer import VectorIndexer
from app.vector.retriever import VectorRetriever

router = APIRouter()


@router.post("/documents", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)) -> IngestResponse:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    temp_file = upload_dir / file.filename
    temp_file.write_bytes(await file.read())
    
    doc_id = Path(file.filename).stem
    from app.vector.indexer import VectorIndexer
    from app.services.vector_service import vector_service
    
    indexer = VectorIndexer(vector_service)
    chunks_count = await indexer.index_pdf(str(temp_file), doc_id)
    
    if temp_file.exists():
        os.remove(temp_file)
        
    return IngestResponse(document_id=doc_id, chunks_indexed=chunks_count)
