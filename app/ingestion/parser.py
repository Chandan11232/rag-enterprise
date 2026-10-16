

class DocumentParser:
    @staticmethod
    def chunk_text(
        text: str, chunk_size: int = 500, chunk_overlap: int = 50
    ) -> list[str]:
        """Splits text into overlapping chunks by words/characters."""
        if not text:
            return []

        words = text.split()
        if not words:
            return []

        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i : i + chunk_size]
            chunks.append(" ".join(chunk_words))
            i += chunk_size - chunk_overlap
            i = max(i, 0)
            if i >= len(words):
                break
        return chunks
