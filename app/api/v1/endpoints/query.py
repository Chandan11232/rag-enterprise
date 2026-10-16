from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.db.vector_store import VectorStore
from app.ingestion.embedder import Embedder
from app.services.llm import OllamaClient
from app.services.reranker import Reranker

router = APIRouter()


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = 5
    rerank_top_k: int = 3
    stream: bool = True


@router.post("/query", status_code=status.HTTP_200_OK)
async def query_rag(payload: QueryRequest, db: AsyncSession = Depends(get_db)):  # noqa: B008
    try:
        # 1. Embed query
        embedder = Embedder.get_instance()
        query_embedding = embedder.embed_text(payload.query)

        # 2. Vector Similarity Search (pgvector)
        candidates = await VectorStore.similarity_search(
            db=db, query_embedding=query_embedding, limit=payload.top_k
        )

        if not candidates:
            if payload.stream:
                async def empty_stream():
                    yield "No relevant context found in the database."
                return StreamingResponse(empty_stream(), media_type="text/plain")
            else:
                return {"answer": "No relevant context found.", "sources": []}

        # 3. Cross-Encoder Reranking
        reranker = Reranker.get_instance()
        ranked_chunks = reranker.rerank(
            query=payload.query, candidates=candidates, top_k=payload.rerank_top_k
        )

        # 4. Prompt Formulation
        context_str = "\n\n---\n\n".join(
            [f"[Source: {c['title']}]\n{c['content']}" for c in ranked_chunks]
        )
        system_prompt = (
            "You are an expert enterprise AI assistant. Answer the user's question accurately "
            "based exclusively on the provided context. If the answer cannot be found in the context, "
            "state clearly that you do not know."
        )
        prompt = f"Context:\n{context_str}\n\nQuestion: {payload.query}\nAnswer:"

        # 5. LLM Generation
        if payload.stream:
            async def response_stream():
                async for chunk in OllamaClient.generate_stream(prompt, system_prompt):
                    yield chunk
            return StreamingResponse(response_stream(), media_type="text/plain")
        else:
            full_response = []
            async for chunk in OllamaClient.generate_stream(prompt, system_prompt):
                full_response.append(chunk)
            return {
                "answer": "".join(full_response),
                "sources": [
                    {"title": c["title"], "source": c["source"], "score": c.get("relevance_score")}
                    for c in ranked_chunks
                ],
            }
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e))
