from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.db.vector_store import VectorStore
from app.ingestion.embedder import Embedder
from app.ingestion.parser import DocumentParser

router = APIRouter()


class IngestRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    source: str | None = None
    content: str = Field(..., min_length=1)
    chunk_size: int = 500
    chunk_overlap: int = 50


class IngestResponse(BaseModel):
    document_id: int
    title: str
    chunks_created: int
    message: str


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(payload: IngestRequest, db: AsyncSession = Depends(get_db)):
    try:
        raw_chunks = DocumentParser.chunk_text(
            payload.content,
            chunk_size=payload.chunk_size,
            chunk_overlap=payload.chunk_overlap,
        )
        if not raw_chunks:
            raise HTTPException(
                status_code=400, detail="Document content resulted in 0 chunks."
            )

        embedder = Embedder.get_instance()
        embeddings = embedder.embed_batch(raw_chunks)

        chunks_data = []
        for idx, (chunk_text, embedding) in enumerate(zip(raw_chunks, embeddings)):
            chunks_data.append(
                {
                    "content": chunk_text,
                    "chunk_index": idx,
                    "embedding": embedding,
                }
            )

        doc = await VectorStore.save_document_chunks(
            db=db, title=payload.title, source=payload.source, chunks_data=chunks_data
        )

        return IngestResponse(
            document_id=doc.id,
            title=doc.title,
            chunks_created=len(chunks_data),
            message="Document successfully ingested and embedded.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
