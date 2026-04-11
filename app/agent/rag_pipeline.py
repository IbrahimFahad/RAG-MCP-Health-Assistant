"""
Main RAG pipeline — entry point for all user queries.
Wires together: language detection → retrieval → agent → disclaimer → follow-ups.
"""
from dotenv import load_dotenv
load_dotenv(override=True)

from app.mcp_tools.language_detector import detect_language
from app.retrieval.search import retrieve, should_use_web
from app.agent.agent_loop import run_agent
from app.mcp_tools.disclaimer_injector import inject_disclaimer
from app.mcp_tools.followup_generator import generate_followups


def process_query(query: str, chat_history: list = None) -> dict:
    """
    Full RAG pipeline for a user health query.

    Args:
        query:        The user's question (Arabic or English).
        chat_history: Previous messages for multi-turn conversation.

    Returns:
        {
            "answer":        str,        # final answer with disclaimer
            "language":      str,        # 'ar' or 'en'
            "source":        str,        # 'database' or 'web'
            "best_score":    float,      # DB similarity score (0 if web)
            "tools_used":    list[str],  # tools Claude called
            "sources":       list[str],  # URLs referenced
            "followups":     list[str],  # 3 suggested follow-up questions
            "tool_rounds":   int,        # agent loop iterations
        }
    """

    # ── Step 1: Detect language ───────────────────────────────────────────────
    language = detect_language(query)
    print(f"[Pipeline] Language: {language}")

    # ── Step 2: Retrieve from vector DB ──────────────────────────────────────
    print(f"[Pipeline] Searching DB...")
    retrieval = retrieve(query)
    print(f"[Pipeline] DB result: found={retrieval['found']}, score={retrieval['best_score']}")

    # ── Step 3: Decide source — DB or web ────────────────────────────────────
    use_web = should_use_web(retrieval)
    source = "web" if use_web else "database"
    print(f"[Pipeline] Source: {source}")

    # ── Step 4: Run agent ─────────────────────────────────────────────────────
    # If DB hit → pass context so Claude doesn't need to search
    # If DB miss → pass no context, Claude will use web_search tool
    db_context = retrieval["context"] if not use_web else ""

    agent_result = run_agent(
        user_query=query,
        db_context=db_context,
        language=language,
        chat_history=chat_history or [],
    )

    raw_answer = agent_result["answer"]
    print(f"[Pipeline] Agent done. Tools used: {agent_result['tools_used']}")

    # ── Step 5: Inject medical disclaimer ────────────────────────────────────
    final_answer = inject_disclaimer(raw_answer, language=language)

    # ── Step 6: Generate follow-up questions ─────────────────────────────────
    followups = generate_followups(query, raw_answer, language=language)

    # ── Step 7: Merge sources ────────────────────────────────────────────────
    all_sources = list(set(retrieval["sources"] + agent_result["sources"]))

    return {
        "answer":      final_answer,
        "language":    language,
        "source":      source,
        "best_score":  retrieval["best_score"],
        "tools_used":  agent_result["tools_used"],
        "sources":     all_sources,
        "followups":   followups,
        "tool_rounds": agent_result["tool_rounds"],
    }
