"""
Restaurant Nutrition Service
Provides local search + Claude AI chat over Saudi restaurant menu data.
"""
import anthropic
from app.config import ANTHROPIC_API_KEY
from app.services.restaurant_nutrition.data import RESTAURANTS

_claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def get_all_restaurants() -> list[dict]:
    return [
        {
            "key": k,
            "name_en": v["name_en"],
            "name_ar": v["name_ar"],
            "category": v["category"],
            "emoji": v["emoji"],
            "color": v["color"],
            "item_count": len(v["items"]),
        }
        for k, v in RESTAURANTS.items()
    ]


def get_restaurant_menu(restaurant_key: str) -> dict | None:
    return RESTAURANTS.get(restaurant_key)


def search_items(query: str, restaurant_key: str = None) -> list[dict]:
    """Keyword search across menu items. Returns items with restaurant info attached."""
    q = query.lower().strip()
    results = []
    scope = {restaurant_key: RESTAURANTS[restaurant_key]} if restaurant_key and restaurant_key in RESTAURANTS else RESTAURANTS
    for key, rest in scope.items():
        for item in rest["items"]:
            if (q in item["name_en"].lower() or
                q in item["name_ar"] or
                q in item["category"].lower() or
                q in rest["name_en"].lower() or
                q in rest["name_ar"]):
                results.append({**item, "restaurant_key": key,
                                 "restaurant_en": rest["name_en"],
                                 "restaurant_ar": rest["name_ar"],
                                 "restaurant_emoji": rest["emoji"]})
    return results


def get_lowest_calorie_items(restaurant_key: str = None, top_n: int = 5) -> list[dict]:
    scope = {restaurant_key: RESTAURANTS[restaurant_key]} if restaurant_key and restaurant_key in RESTAURANTS else RESTAURANTS
    all_items = []
    for key, rest in scope.items():
        for item in rest["items"]:
            if item["category"] in ("Drink", "Sauce"):
                continue
            all_items.append({**item, "restaurant_key": key,
                               "restaurant_en": rest["name_en"],
                               "restaurant_ar": rest["name_ar"],
                               "restaurant_emoji": rest["emoji"]})
    return sorted(all_items, key=lambda x: x["calories"])[:top_n]


def _build_context(restaurant_key: str = None) -> str:
    scope = {restaurant_key: RESTAURANTS[restaurant_key]} if restaurant_key and restaurant_key in RESTAURANTS else RESTAURANTS
    lines = []
    for key, rest in scope.items():
        lines.append(f"\n=== {rest['name_en']} ({rest['name_ar']}) ===")
        for item in rest["items"]:
            lines.append(
                f"  • {item['name_en']} ({item['name_ar']}): "
                f"{item['calories']} kcal | Protein {item['protein_g']}g | "
                f"Carbs {item['carbs_g']}g | Fat {item['fat_g']}g | "
                f"Sodium {item['sodium_mg']}mg | Category: {item['category']}"
            )
    return "\n".join(lines)


def ask_restaurant_ai(question: str, restaurant_key: str = None, language: str = "en") -> dict:
    """
    Ask Claude a question about restaurant nutrition.
    Returns {answer, items_mentioned}
    """
    context = _build_context(restaurant_key)
    rest_name = RESTAURANTS[restaurant_key]["name_en"] if restaurant_key else "all listed Saudi restaurants"

    system = f"""You are a nutrition expert for {rest_name} in Saudi Arabia.
You have access to the complete menu nutrition data below.
Answer the user's question accurately using ONLY the provided data.
Be helpful, specific, and mention exact calorie counts when relevant.
If the user asks in Arabic, respond in Arabic. Otherwise respond in English.
Format numbers clearly. When comparing items, use a concise table or list.

MENU DATA:
{context}

IMPORTANT: This data is approximate. Always recommend users verify with the restaurant directly.
Do NOT add a disclaimer paragraph — keep responses concise and actionable."""

    response = _claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": question}],
        system=system,
    )

    answer = response.content[0].text

    # Find which items were mentioned
    items_mentioned = []
    q_lower = question.lower()
    for key, rest in RESTAURANTS.items():
        if restaurant_key and key != restaurant_key:
            continue
        for item in rest["items"]:
            if item["name_en"].lower() in answer.lower():
                items_mentioned.append({**item,
                                        "restaurant_en": rest["name_en"],
                                        "restaurant_emoji": rest["emoji"]})

    return {"answer": answer, "items_mentioned": items_mentioned[:6]}