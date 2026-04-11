"""
Tool executor — runs the actual tool function when Claude calls it.
Maps tool names to their Python implementations.
"""
from app.mcp_tools.web_search import web_search
from app.mcp_tools.web_scraper import scrape
from app.mcp_tools.pubmed_search import search_pubmed
from app.mcp_tools.store_to_db import store_to_db
from app.mcp_tools.source_validator import validate_source
from app.mcp_tools.health_calculators import (
    calculate_bmi,
    calculate_bmr,
    calculate_ideal_weight,
)


def execute_tool(tool_name: str, tool_input: dict) -> dict:
    """
    Execute a tool by name with the given inputs.
    Returns the tool result as a dict.
    """
    try:
        if tool_name == "web_search":
            results = web_search(
                query=tool_input["query"],
                max_results=tool_input.get("max_results", 5)
            )
            # Filter to trusted sources only
            trusted = [r for r in results if validate_source(r["url"])["trusted"]]
            used = trusted if trusted else results  # fallback to all if none trusted
            return {"results": used, "count": len(used), "filtered_untrusted": len(results) - len(used)}

        elif tool_name == "scrape_url":
            return scrape(url=tool_input["url"])

        elif tool_name == "pubmed_search":
            articles = search_pubmed(
                query=tool_input["query"],
                max_results=tool_input.get("max_results", 3)
            )
            return {"articles": articles, "count": len(articles)}

        elif tool_name == "store_to_db":
            return store_to_db(
                text=tool_input["text"],
                title=tool_input.get("title", ""),
                source_url=tool_input.get("source_url", ""),
                source_type=tool_input.get("source_type", "web"),
            )

        elif tool_name == "calculate_bmi":
            return calculate_bmi(
                weight_kg=tool_input["weight_kg"],
                height_cm=tool_input["height_cm"]
            )

        elif tool_name == "calculate_bmr":
            return calculate_bmr(
                weight_kg=tool_input["weight_kg"],
                height_cm=tool_input["height_cm"],
                age_years=tool_input["age_years"],
                gender=tool_input["gender"],
                activity_level=tool_input.get("activity_level", "moderate")
            )

        elif tool_name == "calculate_ideal_weight":
            return calculate_ideal_weight(
                height_cm=tool_input["height_cm"],
                gender=tool_input["gender"]
            )

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    except Exception as e:
        return {"error": f"Tool '{tool_name}' failed: {str(e)}"}
