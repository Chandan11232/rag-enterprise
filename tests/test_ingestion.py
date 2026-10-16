from app.ingestion.parser import DocumentParser


def test_document_parser_chunking():
    text = "This is a test document. " * 100  # 400 words approximately
    chunks = DocumentParser.chunk_text(text, chunk_size=50, chunk_overlap=10)
    assert len(chunks) > 1
    assert all(isinstance(c, str) for c in chunks)
    assert len(chunks[0].split()) <= 50
