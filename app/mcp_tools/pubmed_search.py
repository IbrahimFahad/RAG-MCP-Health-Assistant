from dotenv import load_dotenv
load_dotenv(override=True)

import requests
import xml.etree.ElementTree as ET

# NIH PubMed API endpoints — completely free, no API key needed
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Tool identification (NIH recommends this for rate limiting)
TOOL_PARAMS = {
    "tool":  "rag-mcp-health",
    "email": "student@university.edu",
}


def search_pubmed(query: str, max_results: int = 3) -> list[dict]:
    """
    Search PubMed for scientific articles related to the query.
    Returns a list of articles with title, abstract, authors, and URL.

    Steps:
        1. esearch — find article IDs matching the query
        2. efetch  — retrieve full details for those IDs
    """

    # Step 1: Search for matching article IDs
    search_params = {
        **TOOL_PARAMS,
        "db":          "pubmed",
        "term":        query,
        "retmax":      max_results,
        "retmode":     "json",
        "sort":        "relevance",
    }

    search_response = requests.get(ESEARCH_URL, params=search_params, timeout=15)
    search_response.raise_for_status()
    search_data = search_response.json()

    ids = search_data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []

    # Step 2: Fetch full article details for those IDs
    fetch_params = {
        **TOOL_PARAMS,
        "db":      "pubmed",
        "id":      ",".join(ids),
        "retmode": "xml",
        "rettype": "abstract",
    }

    fetch_response = requests.get(EFETCH_URL, params=fetch_params, timeout=15)
    fetch_response.raise_for_status()

    return _parse_pubmed_xml(fetch_response.text)


def _parse_pubmed_xml(xml_text: str) -> list[dict]:
    """Parse PubMed XML response into clean article dicts."""
    root = ET.fromstring(xml_text)
    articles = []

    for article in root.findall(".//PubmedArticle"):
        # Title
        title_el = article.find(".//ArticleTitle")
        title = title_el.text if title_el is not None else "No title"

        # Abstract (may have multiple sections)
        abstract_parts = article.findall(".//AbstractText")
        abstract = " ".join(
            (el.text or "") for el in abstract_parts if el.text
        ).strip()

        # Authors
        author_els = article.findall(".//Author")
        authors = []
        for a in author_els[:3]:  # first 3 authors only
            last  = a.findtext("LastName", "")
            first = a.findtext("ForeName", "")
            if last:
                authors.append(f"{last} {first}".strip())
        author_str = ", ".join(authors) + (" et al." if len(author_els) > 3 else "")

        # PubMed ID and URL
        pmid_el = article.find(".//PMID")
        pmid = pmid_el.text if pmid_el is not None else ""
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""

        # Year
        year_el = article.find(".//PubDate/Year")
        year = year_el.text if year_el is not None else ""

        if abstract:  # only include articles that have an abstract
            articles.append({
                "pmid":     pmid,
                "title":    title,
                "abstract": abstract,
                "authors":  author_str,
                "year":     year,
                "url":      url,
            })

    return articles
