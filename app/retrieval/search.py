from dotenv import load_dotenv
load_dotenv(override=True)

from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY, SIMILARITY_THRESHOLD, TOP_K_RESULTS
from app.embeddings.embedder import embed_query

_client = None

def get_client():
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def search(query: str, threshold: float = None, top_k: int = None) -> list[dict]:
    """
    Embed the query and search Supabase for similar health knowledge.

    Returns list of matching rows with similarity scores.
    Empty list means nothing was found above the threshold.
    """
    if threshold is None:
        threshold = SIMILARITY_THRESHOLD
    if top_k is None:
        top_k = TOP_K_RESULTS

    client = get_client()
    query_vector = embed_query(query)

    result = client.rpc("search_health_knowledge", {
        "query_embedding": query_vector,
        "match_threshold": threshold,
        "match_count": top_k,
    }).execute()

    return result.data


# ── Step 27: Retrieval function ───────────────────────────────────────────────

def retrieve(query: str) -> dict:
    """
    Main retrieval function used by the agent.

    Embeds the query, searches Supabase, and returns a structured result
    that tells the agent whether the DB had a good answer or not.

    Returns:
        {
            "found":       bool,        # True if DB hit above threshold
            "results":     list[dict],  # matched chunks with scores
            "best_score":  float,       # highest similarity score found
            "context":     str,         # combined text of top results (for Claude)
            "sources":     list[str],   # source URLs of matched chunks
        }
    """
    results = search(query)

    if not results:
        return {
            "found":      False,
            "results":    [],
            "best_score": 0.0,
            "context":    "",
            "sources":    [],
        }

    # Build a single context string from all matched chunks
    context_parts = []
    sources = []
    for r in results:
        context_parts.append(r["content"])
        if r.get("source_url"):
            sources.append(r["source_url"])

    return {
        "found":      True,
        "results":    results,
        "best_score": round(results[0]["similarity"], 4),
        "context":    "\n\n---\n\n".join(context_parts),
        "sources":    list(dict.fromkeys(sources)),   # deduplicate, preserve order
    }


# ── Step 28: Similarity threshold checker ────────────────────────────────────

def should_use_web(retrieval_result: dict, confidence_threshold: float = None) -> bool:
    """
    Decide whether to use the DB answer or fall back to web search.

    Returns True  → DB miss, agent should search the web.
    Returns False → DB hit, agent can answer from DB context.

    Logic:
        - Not found in DB at all          → use web
        - Best score below threshold      → use web
        - Found but very short context    → use web (low quality hit)
    """
    if confidence_threshold is None:
        confidence_threshold = SIMILARITY_THRESHOLD

    if not retrieval_result["found"]:
        return True

    if retrieval_result["best_score"] < confidence_threshold:
        return True

    # Treat very short context as a low-quality hit and fall back to web
    if len(retrieval_result["context"].strip()) < 50:
        return True

    return False
