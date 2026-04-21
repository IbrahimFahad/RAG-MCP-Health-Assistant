"""
Agent loop — the brain of the system.
Sends the user query to Claude, handles tool calls, and returns the final answer.
"""
from dotenv import load_dotenv
load_dotenv(override=True)

import re
import json
import anthropic

from app.config import ANTHROPIC_API_KEY
from app.agent.tool_definitions import TOOL_DEFINITIONS
from app.agent.tool_executor import execute_tool

MAX_QUERY_LENGTH = 2000

def _sanitize_input(text: str) -> str:
    """Strip control characters and cap length to prevent prompt injection."""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text[:MAX_QUERY_LENGTH].strip()

_client = None

def get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


# ── Step 34: System prompt ────────────────────────────────────────────────────

BASE_SYSTEM_PROMPT = """You are a knowledgeable and trustworthy health assistant. You help users understand medical topics, symptoms, treatments, and healthy lifestyle choices.

Core rules:
- CRITICAL: You MUST respond in {language_instruction}. This is mandatory regardless of the language of any context or retrieved content.
- Be clear, accurate, and compassionate
- Use the tools available to find information when needed
- After retrieving information from web_search or pubmed_search, ALWAYS call store_to_db to save it for future use
- For clinical questions, prefer PubMed articles over general web results
- Never diagnose or prescribe — always recommend consulting a doctor for personal medical decisions
- If context is provided from the knowledge base, use it as your primary source but respond in {language_instruction}

Tool usage strategy:
1. If no context is provided → use web_search and/or pubmed_search to find information
2. After finding information → call store_to_db to save it
3. For calculator questions (BMI, calories, weight) → call the appropriate calculator tool directly"""

def build_system_prompt(language: str) -> str:
    """Build system prompt with explicit language instruction."""
    if language == "ar":
        lang_instruction = "Arabic (العربية) — your entire response must be in Arabic"
    else:
        lang_instruction = "English — your entire response must be in English"
    return BASE_SYSTEM_PROMPT.format(language_instruction=lang_instruction)


# ── Steps 30 & 35: Agent loop + tool call handling ───────────────────────────

def run_agent(
    user_query: str,
    db_context: str = "",
    language: str = "en",
    chat_history: list = None,
    max_tool_rounds: int = 5,
) -> dict:
    """
    Run the agent loop for a user query.

    Args:
        user_query:      The user's health question.
        db_context:      Pre-retrieved context from vector DB (if any).
        language:        'en' or 'ar' — enforces response language.
        chat_history:    Previous messages for multi-turn conversation (Step 36).
        max_tool_rounds: Max tool call rounds to prevent infinite loops.

    Returns:
        {
            "answer":       str,         # Claude's final answer
            "tools_used":   list[str],   # names of tools that were called
            "sources":      list[str],   # URLs used
            "tool_rounds":  int,         # how many tool rounds happened
        }
    """
    client = get_client()
    system_prompt = build_system_prompt(language)
    user_query = _sanitize_input(user_query)

    # Build the initial user message
    if db_context:
        user_message = (
            f"Context from knowledge base:\n{db_context}\n\n"
            f"User question: {user_query}"
        )
    else:
        user_message = user_query

    # Step 36: multi-turn — start with history or fresh
    messages = list(chat_history) if chat_history else []
    messages.append({"role": "user", "content": user_message})

    tools_used = []
    sources = []
    tool_rounds = 0

    # Agent loop — keep going until Claude gives a final text answer
    while tool_rounds < max_tool_rounds:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_prompt,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Step 35: Claude gave a final text answer — done
        if response.stop_reason == "end_turn":
            final_answer = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_answer += block.text
            return {
                "answer":      final_answer,
                "tools_used":  tools_used,
                "sources":     list(set(sources)),
                "tool_rounds": tool_rounds,
            }

        # Step 35: Claude wants to call tools
        if response.stop_reason == "tool_use":
            tool_rounds += 1

            # Add Claude's response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Process each tool call
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                tool_name  = block.name
                tool_input = block.input
                tools_used.append(tool_name)

                print(f"  [Tool] {tool_name}({json.dumps(tool_input)[:80]}...)")

                # Execute the tool
                result = execute_tool(tool_name, tool_input)

                # Track sources
                if tool_name == "web_search":
                    sources += [r["url"] for r in result.get("results", [])]
                elif tool_name == "scrape_url":
                    sources.append(tool_input.get("url", ""))
                elif tool_name == "pubmed_search":
                    sources += [a["url"] for a in result.get("articles", [])]

                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     json.dumps(result),
                })

            # Send tool results back to Claude
            messages.append({"role": "user", "content": tool_results})

    # Fallback if max rounds exceeded
    return {
        "answer":      "I was unable to find a complete answer. Please try rephrasing your question.",
        "tools_used":  tools_used,
        "sources":     list(set(sources)),
        "tool_rounds": tool_rounds,
    }