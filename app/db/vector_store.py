from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk, Document


class VectorStore:
    @staticmethod
    async def save_document_chunks(
        db: AsyncSession, title: str, source: str, chunks_data: list[dict[str, Any]]
    ) -> Document:
        doc = Document(title=title, source=source)
        db.add(doc)
        await db.flush()  # get doc.id

        for item in chunks_data:
            chunk = Chunk(
                document_id=doc.id,
                content=item["content"],
                chunk_index=item["chunk_index"],
                embedding=item["embedding"],
            )
            db.add(chunk)

        await db.commit()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def similarity_search(
        db: AsyncSession, query_embedding: list[float], limit: int = 5
    ) -> list[dict[str, Any]]:
        # Using pgvector cosine distance operator <=>
        stmt = (
            select(Chunk, Document)
            .join(Document, Chunk.document_id == Document.id)
            .order_by(Chunk.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.all()

        matches = []
        for chunk, doc in rows:
            matches.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": doc.id,
                    "title": doc.title,
                    "source": doc.source,
                    "content": chunk.content,
                    "chunk_index": chunk.chunk_index,
                }
            )
        return matches
