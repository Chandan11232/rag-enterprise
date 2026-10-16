from typing import Any

from sentence_transformers import CrossEncoder

from app.core.config import settings


class Reranker:
    _instance = None

    def __init__(self):
        self.model = CrossEncoder(settings.RERANKER_MODEL)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def rerank(
        self, query: str, candidates: list[dict[str, Any]], top_k: int = 3
    ) -> list[dict[str, Any]]:
        if not candidates:
            return []

        pairs = [[query, c["content"]] for c in candidates]
        scores = self.model.predict(pairs)

        for i, score in enumerate(scores):
            candidates[i]["relevance_score"] = float(score)

        candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
        return candidates[:top_k]
