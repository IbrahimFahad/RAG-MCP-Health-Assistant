"""
Medicine Information Service.
1. Vector search in medicine_knowledge table (separate from health_knowledge).
2. FDA Drug Label API fallback if DB has no relevant data.
3. Tavily web search fallback if FDA also returns nothing.
4. Claude synthesises an answer from whatever context was found.
"""
from dotenv import load_dotenv
load_dotenv(override=True)

import anthropic
from app.config import ANTHROPIC_API_KEY
from app.mcp_tools.language_detector import detect_language
from app.mcp_tools.disclaimer_injector import inject_disclaimer
from app.mcp_tools.followup_generator import generate_followups
from app.mcp_tools.web_search import web_search
from app.services.medicine_db import (
    search_medicine,
    search_fda,
    format_fda_context,
    store_medicine_chunks,
)

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


# ── Ingestion helpers (used by ingest_medicines.py script only) ───────────────

def ingest_medicine_text(text: str, title: str) -> dict:
    """Store plain medicine text into medicine_knowledge table."""
    n = store_medicine_chunks(text, title=title)
    return {"status": "success", "title": title, "chunks": n}


def ingest_medicine_file(file_path: str, title: str = "") -> dict:
    """Load a PDF or .txt medicine file, chunk, and store."""
    import fitz, os
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        doc = fitz.open(file_path)
        text = "\n\n".join(p.get_text("text").strip() for p in doc if p.get_text("text").strip())
        doc.close()
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    name = title or os.path.splitext(os.path.basename(file_path))[0].replace("_", " ").title()
    n = store_medicine_chunks(text, title=name)
    return {"status": "success", "file": file_path, "chunks": n}


# ── Main Q&A function ─────────────────────────────────────────────────────────

def answer_medicine_question(question: str, history: list = None) -> dict:
    """
    Answer a medicine question.
    Pipeline:
      1. Vector search in medicine_knowledge table
      2. If no DB hit → FDA Drug Label API fallback
      3. Claude answers from whatever context was found
      4. Disclaimer + follow-up questions appended

    Returns:
        {
            "answer":      str,
            "followups":   list[str],
            "sources":     list[str],
            "language":    'ar' | 'en',
            "source_type": 'database' | 'fda_api' | 'none'
        }
    """
    if history is None:
        history = []

    lang = detect_language(question)

    # ── Step 1: Vector DB search ──────────────────────────────────────────────
    db_results  = search_medicine(question, threshold=0.45, top_k=5)
    context     = ""
    sources     = []
    source_type = "none"

    if db_results:
        parts = []
        for chunk in db_results:
            content = chunk.get("content", "").strip()
            title   = chunk.get("title", "").strip()
            if content:
                parts.append(f"[{title}]\n{content}" if title else content)
                if title and title not in sources:
                    sources.append(title)
        context     = "\n\n---\n\n".join(parts)
        source_type = "database"

    # ── Step 2: FDA API fallback ──────────────────────────────────────────────
    if not context:
        fda_data = search_fda(question)
        if fda_data:
            context     = format_fda_context(fda_data)
            sources     = [fda_data.get("source", "FDA API")]
            source_type = "fda_api"

    # ── Step 3: Web search fallback ───────────────────────────────────────────
    if not context:
        try:
            pil_query   = f"{question} patient information leaflet side effects dosage"
            web_results = web_search(pil_query)
            parts       = []
            web_sources = []
            for r in web_results[:4]:
                snippet = r.get("content", r.get("snippet", "")).strip()
                url     = r.get("url", "")
                if snippet:
                    parts.append(snippet[:800])
                if url:
                    web_sources.append(url)
            if parts:
                context     = "\n\n---\n\n".join(parts)
                sources     = web_sources
                source_type = "web_search"
        except Exception:
            pass

    # ── Step 4: Build Claude prompt ───────────────────────────────────────────
    if lang == "ar":
        system_prompt = (
            "أنت مساعد صيدلاني متخصص. "
            "أجب على سؤال المستخدم بناءً على السياق المتاح فقط. "
            "إذا لم تكن المعلومات موجودة، قل ذلك بوضوح ولا تخترع أي معلومات. "
            "نظّم إجابتك بشكل واضح. أجب باللغة العربية دائماً."
        )
    else:
        system_prompt = (
            "You are a pharmaceutical assistant. "
            "Answer the user's question based only on the context provided. "
            "If the information is not present, say so clearly — do not fabricate. "
            "Structure your answer with headings when the response is long. "
            "Always respond in English."
        )

    if context:
        user_content = (
            f"المعلومات المتاحة:\n\n{context}\n\n---\n\nالسؤال: {question}"
            if lang == "ar" else
            f"Available information:\n\n{context}\n\n---\n\nQuestion: {question}"
        )
    else:
        user_content = (
            f"لم يتم العثور على معلومات عن هذا الدواء في قاعدة البيانات أو FDA. السؤال: {question}"
            if lang == "ar" else
            f"No information found for this medicine in the database or FDA. Question: {question}"
        )

    messages = list(history)
    messages.append({"role": "user", "content": user_content})

    response = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )

    answer_text            = response.content[0].text
    answer_with_disclaimer = inject_disclaimer(answer_text, lang)
    followups              = generate_followups(question, answer_text, lang)

    return {
        "answer":      answer_with_disclaimer,
        "followups":   followups,
        "sources":     sources,
        "language":    lang,
        "source_type": source_type,
    }