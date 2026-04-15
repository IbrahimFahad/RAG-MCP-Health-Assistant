"""
Medicine-specific vector DB operations.
Uses the 'medicine_knowledge' table — completely separate from 'health_knowledge'.
"""
from dotenv import load_dotenv
load_dotenv(override=True)

import requests
from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY
from app.embeddings.embedder import embed_query, embed_passage
from app.embeddings.chunker import chunk_text

_sb = None

def _get_sb():
    global _sb
    if _sb is None:
        _sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _sb


# ── Store ─────────────────────────────────────────────────────────────────────

def store_medicine_chunks(text: str, title: str = "", source_url: str = "") -> int:
    """Chunk, embed, and insert into medicine_knowledge. Returns number of chunks stored."""
    sb = _get_sb()
    chunks = chunk_text(text)
    rows = []
    for chunk in chunks:
        embedding = embed_passage(chunk)
        rows.append({
            "content":    chunk,
            "embedding":  embedding,
            "title":      title,
            "source_url": source_url,
        })
    if rows:
        sb.table("medicine_knowledge").insert(rows).execute()
    return len(rows)


# ── Search ────────────────────────────────────────────────────────────────────

def _extract_medicine_name(query: str) -> str:
    """Best-effort: return the first capitalised word(s) that look like a drug name."""
    import re
    # Strip common question words and grab the first multi-char capitalised token
    stopwords = {"what", "is", "are", "the", "can", "i", "take", "for", "about",
                 "tell", "me", "my", "how", "dose", "dosage", "side", "effects",
                 "uses", "use", "of", "a", "an", "this", "drug", "medicine"}
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-]+", query)
    for tok in tokens:
        if tok.lower() not in stopwords and len(tok) >= 3:
            return tok
    return query.split()[0] if query.split() else query


def search_medicine_by_title(name: str) -> list[dict]:
    """
    Text search on the title column (case-insensitive).
    Returns rows whose title contains the medicine name.
    Much faster than vector search and more precise for known names.
    """
    sb = _get_sb()
    try:
        result = (
            sb.table("medicine_knowledge")
            .select("id, content, title, source_url")
            .ilike("title", f"%{name}%")
            .limit(6)
            .execute()
        )
        # Normalise shape to match vector search results
        rows = []
        for r in (result.data or []):
            r["similarity"] = 1.0  # exact title match — treat as perfect score
            rows.append(r)
        return rows
    except Exception:
        return []


def search_medicine(query: str, threshold: float = 0.45, top_k: int = 5) -> list[dict]:
    """
    Two-step search:
      1. Try exact title match (fast, precise).
      2. Fall back to vector similarity search if no title hit.
    """
    # Step 1: title search using extracted medicine name
    name = _extract_medicine_name(query)
    title_hits = search_medicine_by_title(name)
    if title_hits:
        return title_hits

    # Step 2: vector search
    sb = _get_sb()
    vector = embed_query(query)
    result = sb.rpc(
        "search_medicine_knowledge",
        {
            "query_embedding": vector,
            "match_threshold":  threshold,
            "match_count":      top_k,
        }
    ).execute()
    return result.data or []


# ── FDA Label API fallback ────────────────────────────────────────────────────

def _fda_label_search(term: str, field: str) -> dict | None:
    url = (
        f"https://api.fda.gov/drug/label.json"
        f"?search=openfda.{field}:\"{term}\"&limit=1"
    )
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            results = resp.json().get("results")
            if results:
                return results[0]
    except Exception:
        pass
    return None


def _fda_event_search(medicine_name: str) -> dict | None:
    """Fallback: search adverse events API."""
    url = (
        f"https://api.fda.gov/drug/event.json"
        f"?search=patient.drug.medicinalproduct:\"{medicine_name}\"&limit=3"
    )
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            results = resp.json().get("results")
            if results:
                return results
    except Exception:
        pass
    return None


def _extract_field(obj, *keys) -> str:
    """Safely extract a field that may be a list or string."""
    for key in keys:
        val = obj.get(key)
        if val:
            if isinstance(val, list):
                return " ".join(val)[:1500]
            return str(val)[:1500]
    return ""


def search_fda(medicine_name: str) -> dict | None:
    """
    Query FDA drug label API for medicine info.
    Tries brand_name first, then generic_name, then full-text search.
    Falls back to adverse events API if label not found.
    Returns a structured dict or None if nothing found.
    """
    label = (
        _fda_label_search(medicine_name, "brand_name")
        or _fda_label_search(medicine_name, "generic_name")
    )

    # Full-text label search as last label attempt
    if not label:
        try:
            url = f"https://api.fda.gov/drug/label.json?search=\"{medicine_name}\"&limit=1"
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                results = resp.json().get("results")
                if results:
                    label = results[0]
        except Exception:
            pass

    if label:
        openfda = label.get("openfda", {})
        return {
            "source":            "FDA Drug Label",
            "brand_name":        _extract_field(openfda, "brand_name"),
            "generic_name":      _extract_field(openfda, "generic_name"),
            "indications":       _extract_field(label, "indications_and_usage"),
            "dosage":            _extract_field(label, "dosage_and_administration"),
            "warnings":          _extract_field(label, "warnings", "warnings_and_cautions", "boxed_warning"),
            "side_effects":      _extract_field(label, "adverse_reactions"),
            "contraindications": _extract_field(label, "contraindications"),
            "drug_interactions": _extract_field(label, "drug_interactions"),
        }

    # Last resort — adverse events
    events = _fda_event_search(medicine_name)
    if events:
        reactions = []
        for ev in events:
            for r in ev.get("patient", {}).get("reaction", []):
                pt = r.get("reactionmeddrapt", "")
                if pt and pt not in reactions:
                    reactions.append(pt)
        if reactions:
            return {
                "source":       "FDA Adverse Events",
                "brand_name":   medicine_name,
                "generic_name": "",
                "side_effects": ", ".join(reactions[:20]),
                "indications": "", "dosage": "",
                "warnings": "", "contraindications": "", "drug_interactions": "",
            }

    return None


def format_fda_context(fda: dict) -> str:
    """Convert FDA result dict into a text block Claude can use as context."""
    parts = [f"Source: {fda['source']}"]
    if fda.get("brand_name"):
        parts.append(f"Brand name: {fda['brand_name']}")
    if fda.get("generic_name"):
        parts.append(f"Generic name: {fda['generic_name']}")
    for label, key in [
        ("Indications / Uses", "indications"),
        ("Dosage",             "dosage"),
        ("Warnings",           "warnings"),
        ("Side effects",       "side_effects"),
        ("Contraindications",  "contraindications"),
        ("Drug interactions",  "drug_interactions"),
    ]:
        val = fda.get(key, "").strip()
        if val:
            parts.append(f"\n{label}:\n{val}")
    return "\n".join(parts)