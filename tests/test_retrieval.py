from app.ingestion.embedder import Embedder
from app.services.reranker import Reranker


def test_embedder_dimensions():
    embedder = Embedder.get_instance()
    embedding = embedder.embed_text("Hello enterprise AI")
    assert isinstance(embedding, list)
    assert len(embedding) == 384


def test_reranker_scoring():
    reranker = Reranker.get_instance()
    query = "What is enterprise RAG?"
    candidates = [
        {"content": "Irrelevant text about cooking recipes."},
        {"content": "Enterprise RAG combines vector search with local LLMs."},
    ]
    ranked = reranker.rerank(query, candidates, top_k=1)
    assert len(ranked) == 1
    assert "Enterprise RAG" in ranked[0]["content"]
    assert "relevance_score" in ranked[0]
