from dotenv import load_dotenv
load_dotenv(override=True)

from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY

_client = None

def get_client():
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client

def store_chunks(chunks: list[dict]) -> list[int]:
    """
    Store a list of embedded chunks into the health_knowledge table.

    Each chunk dict must have:
        - content (str)
        - embedding (list[float], 1024 dims)
        - source_url (str)
        - title (str)
        - language (str)
        - source_type (str)
        - metadata (dict)

    Returns list of inserted row IDs.
    """
    client = get_client()
    inserted_ids = []

    for i, chunk in enumerate(chunks):
        row = {
            "content":     chunk["content"],
            "embedding":   chunk["embedding"],
            "source_url":  chunk.get("source_url", ""),
            "title":       chunk.get("title", ""),
            "language":    chunk.get("language", ""),
            "source_type": chunk.get("source_type", "manual"),
            "metadata":    chunk.get("metadata", {}),
        }
        result = client.table("health_knowledge").insert(row).execute()
        inserted_id = result.data[0]["id"]
        inserted_ids.append(inserted_id)
        print(f"  Stored chunk {i+1}/{len(chunks)} -> id: {inserted_id}")

    return inserted_ids

def ingest_file(file_path: str) -> list[int]:
    """
    Full pipeline: load file → chunk → embed → store to Supabase.
    Returns list of inserted row IDs.
    """
    from app.embeddings.pipeline import load_and_chunk
    print(f"Ingesting: {file_path}")
    chunks = load_and_chunk(file_path)
    print(f"Storing {len(chunks)} chunks to Supabase...")
    ids = store_chunks(chunks)
    print(f"Done. Inserted {len(ids)} rows.")
    return ids

def ingest_text(text: str, title: str = "manual", source: str = "manual") -> list[int]:
    """
    Full pipeline for raw text (web scrape, etc): chunk → embed → store.
    Returns list of inserted row IDs.
    """
    from app.embeddings.pipeline import load_and_chunk_string
    print(f"Ingesting text: '{title}'")
    chunks = load_and_chunk_string(text, title=title, source=source)
    print(f"Storing {len(chunks)} chunks to Supabase...")
    ids = store_chunks(chunks)
    print(f"Done. Inserted {len(ids)} rows.")
    return ids
