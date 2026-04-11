from dotenv import load_dotenv
load_dotenv(override=True)

from tavily import TavilyClient
from app.config import TAVILY_API_KEY

_client = None

def get_client() -> TavilyClient:
    global _client
    if _client is None:
        _client = TavilyClient(api_key=TAVILY_API_KEY)
    return _client

def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using Tavily API.
    Automatically focuses on health-related results.

    Returns list of results, each with:
        - title
        - url
        - content (clean text snippet)
        - score (relevance score from Tavily)
    """
    client = get_client()

    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced",   # deeper search, better quality
        include_answer=False,      # we generate our own answer via Claude
        include_raw_content=False, # clean snippets only
    )

    results = []
    for r in response.get("results", []):
        results.append({
            "title":   r.get("title", ""),
            "url":     r.get("url", ""),
            "content": r.get("content", ""),
            "score":   r.get("score", 0.0),
        })

    return results
