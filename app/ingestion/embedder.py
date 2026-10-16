
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class Embedder:
    _instance = None

    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def embed_text(self, text: str) -> list[float]:
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
