from app.embeddings.loader import load_document, load_from_string, Document
from app.embeddings.chunker import chunk_text
from app.embeddings.embedder import embed_passage

def load_and_chunk(file_path: str) -> list[dict]:
    """Load a document from file, chunk it, and embed each chunk."""
    doc = load_document(file_path)
    return _chunk_and_embed(doc)

def load_and_chunk_string(text: str, title: str = "manual", source: str = "manual") -> list[dict]:
    """Chunk and embed text from a string (web scrape, API result, etc)."""
    doc = load_from_string(text, title=title, source=source)
    return _chunk_and_embed(doc)

def _chunk_and_embed(doc: Document) -> list[dict]:
    chunks = chunk_text(doc.text)
    result = []
    for i, chunk in enumerate(chunks):
        print(f"  Embedding chunk {i+1}/{len(chunks)}...")
        result.append({
            "content": chunk,
            "embedding": embed_passage(chunk),
            "source_url": doc.source,
            "title": doc.title,
            "language": doc.language,
            "source_type": doc.metadata.get("file_type", "manual"),
            "metadata": doc.metadata,
        })
    return result
