from dotenv import load_dotenv
load_dotenv(override=True)

from app.retrieval.store import ingest_text


def store_to_db(
    text: str,
    title: str = "",
    source_url: str = "",
    language: str = "",
    source_type: str = "web",
) -> dict:
    """
    MCP tool: embed text and store it in the health knowledge vector DB.
    Called by the agent after scraping or retrieving new content.

    Args:
        text:        The health content to store.
        title:       Article or page title.
        source_url:  Where the content came from.
        language:    'ar' or 'en' (leave empty to auto-detect later).
        source_type: 'web', 'pubmed', 'pdf', or 'manual'.

    Returns:
        {
            "success":       bool,
            "inserted_ids":  list[int],
            "chunks_stored": int,
            "error":         str  (only if success is False)
        }
    """
    if not text or len(text.strip()) < 50:
        return {
            "success": False,
            "inserted_ids": [],
            "chunks_stored": 0,
            "error": "Text too short to store (min 50 chars)."
        }

    try:
        ids = ingest_text(
            text=text,
            title=title,
            source=source_url,
        )
        return {
            "success": True,
            "inserted_ids": ids,
            "chunks_stored": len(ids),
            "error": ""
        }
    except Exception as e:
        return {
            "success": False,
            "inserted_ids": [],
            "chunks_stored": 0,
            "error": str(e)
        }
