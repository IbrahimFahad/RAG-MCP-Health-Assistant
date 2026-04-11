from dotenv import load_dotenv
load_dotenv(override=True)

import requests
from bs4 import BeautifulSoup
from app.config import FIRECRAWL_API_KEY

# Tags that contain noise — not article content
NOISE_TAGS = [
    "nav", "header", "footer", "aside", "script",
    "style", "form", "button", "iframe", "ads",
    "advertisement", "cookie", "popup"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_with_beautifulsoup(url: str) -> str:
    """
    Fetch a URL and extract clean article text using BeautifulSoup.
    Removes navigation, footers, scripts, and other noise.
    """
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove noisy tags
    for tag in soup(NOISE_TAGS):
        tag.decompose()

    # Try to find the main article content first
    main_content = (
        soup.find("article") or
        soup.find("main") or
        soup.find(id="content") or
        soup.find(class_="content") or
        soup.find(class_="article-body") or
        soup.find(class_="post-body") or
        soup.body
    )

    if main_content is None:
        return ""

    # Extract text, collapse whitespace
    lines = [line.strip() for line in main_content.get_text(separator="\n").splitlines()]
    clean_lines = [line for line in lines if len(line) > 30]
    return "\n".join(clean_lines)


def scrape_with_firecrawl(url: str) -> str:
    """
    Scrape using Firecrawl API - handles JavaScript-rendered pages.
    Falls back to this when BeautifulSoup returns too little text.
    """
    if not FIRECRAWL_API_KEY or FIRECRAWL_API_KEY.startswith("your_"):
        raise ValueError("Firecrawl API key not set.")

    from firecrawl import FirecrawlApp
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    result = app.scrape_url(url, formats=["markdown"])
    return result.get("markdown", "")


def scrape(url: str, min_length: int = 200) -> dict:
    """
    Scrape a URL and return clean text + metadata.
    Tries BeautifulSoup first, falls back to Firecrawl if result is too short.

    Returns:
        {
            "url": str,
            "text": str,
            "method": str,   # 'beautifulsoup' or 'firecrawl'
            "success": bool,
            "error": str     # only if success is False
        }
    """
    bs_error = ""
    try:
        text = scrape_with_beautifulsoup(url)
        if len(text) >= min_length:
            return {"url": url, "text": text, "method": "beautifulsoup", "success": True}
        bs_error = f"Too short ({len(text)} chars)"
    except Exception as e:
        bs_error = str(e)

    # Fallback to Firecrawl
    try:
        text = scrape_with_firecrawl(url)
        if len(text) >= min_length:
            return {"url": url, "text": text, "method": "firecrawl", "success": True}
        return {"url": url, "text": "", "method": "firecrawl", "success": False, "error": "Content too short"}
    except Exception as e:
        return {"url": url, "text": "", "method": "none", "success": False, "error": f"BS4: {bs_error} | Firecrawl: {e}"}
