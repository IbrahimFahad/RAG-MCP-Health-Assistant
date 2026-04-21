"""
Restaurant Nutrition Service
Queries the restaurant_menu Supabase table directly.
Claude is only used to format answers — all nutrition data comes from the DB.
"""
import anthropic
from supabase import create_client
from app.config import ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_KEY
from app.services.restaurant_nutrition.data import RESTAURANTS

_claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
_supa = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE = "restaurant_menu"


# ── Read helpers ──────────────────────────────────────────────────────────────

def get_restaurant_menu(restaurant_key: str) -> dict | None:
    """Return restaurant metadata dict from data.py (name, emoji, color, etc.)."""
    return RESTAURANTS.get(restaurant_key)


def get_all_restaurants() -> list[dict]:
    """Return restaurant metadata (no DB call needed — sourced from data.py)."""
    return [
        {
            "key":        k,
            "name_en":    v["name_en"],
            "name_ar":    v["name_ar"],
            "category":   v["category"],
            "emoji":      v["emoji"],
            "color":      v["color"],
            "item_count": len(v["items"]),
        }
        for k, v in RESTAURANTS.items()
    ]


def get_restaurant_items(restaurant_key: str) -> list[dict]:
    """Fetch all items for one restaurant from DB."""
    res = (_supa.table(TABLE)
           .select("*")
           .eq("restaurant_key", restaurant_key)
           .order("calories")
           .execute())
    return res.data


def search_items(query: str, restaurant_key: str = None) -> list[dict]:
    """
    Case-insensitive keyword search on item_name and item_name_ar.
    Optionally scoped to one restaurant.
    """
    q = query.strip()
    builder = (_supa.table(TABLE)
               .select("*")
               .ilike("item_name", f"%{q}%"))
    if restaurant_key:
        builder = builder.eq("restaurant_key", restaurant_key)
    res = builder.order("calories").execute()

    # Also search Arabic name
    builder_ar = (_supa.table(TABLE)
                  .select("*")
                  .ilike("item_name_ar", f"%{q}%"))
    if restaurant_key:
        builder_ar = builder_ar.eq("restaurant_key", restaurant_key)
    res_ar = builder_ar.order("calories").execute()

    # Merge & deduplicate by id
    seen = set()
    combined = []
    for row in (res.data + res_ar.data):
        if row["id"] not in seen:
            seen.add(row["id"])
            combined.append(row)
    return sorted(combined, key=lambda x: x["calories"])


def get_lowest_calorie_items(restaurant_key: str = None, top_n: int = 10) -> list[dict]:
    """Return lowest-calorie items, excluding drinks and sauces."""
    builder = (_supa.table(TABLE)
               .select("*")
               .not_.in_("item_category", ["Drink", "Sauce"])
               .order("calories")
               .limit(top_n))
    if restaurant_key:
        builder = builder.eq("restaurant_key", restaurant_key)
    res = builder.execute()
    return res.data


def get_all_items_for_restaurant(restaurant_key: str) -> list[dict]:
    return get_restaurant_items(restaurant_key)


# ── AI chat (data comes from DB, Claude only formats the answer) ──────────────

def ask_restaurant_ai(question: str, restaurant_key: str = None, language: str = "en") -> dict:
    """
    1. Pull relevant rows from restaurant_menu table.
    2. Pass them as context to Claude — Claude does NOT generate nutrition data.
    3. Return the formatted answer + matched items.
    """
    # Fetch data from DB
    if restaurant_key:
        items = get_restaurant_items(restaurant_key)
        rest_info = RESTAURANTS.get(restaurant_key, {})
        rest_name = rest_info.get("name_en", restaurant_key)
    else:
        res = _supa.table(TABLE).select("*").execute()
        items = res.data
        rest_name = "all listed Saudi restaurants"

    if not items:
        no_data = "لا توجد بيانات متاحة لهذا المطعم." if language == "ar" else "No data available for this restaurant."
        return {"answer": no_data, "items_mentioned": []}

    # Build context string from DB rows
    lines = []
    for r in items:
        lines.append(
            f"{r['restaurant_name']} | {r['item_name']} ({r['item_name_ar']}) | "
            f"Category: {r['item_category']} | "
            f"Calories: {r['calories']} kcal | Protein: {r['protein_g']}g | "
            f"Carbs: {r['carbs_g']}g | Fat: {r['fat_g']}g | Sodium: {r['sodium_mg']}mg"
        )
    context = "\n".join(lines)

    system = f"""You are a nutrition assistant for {rest_name} in Saudi Arabia.
The EXACT nutrition data from our database is provided below — use ONLY these numbers.
Do NOT invent or estimate any values. If something is not in the data, say so.
Answer concisely. Use tables or lists when comparing multiple items.
If the question is in Arabic, answer in Arabic.

DATABASE RECORDS:
{context}"""

    response = _claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        messages=[{"role": "user", "content": question}],
        system=system,
    )
    answer = response.content[0].text

    # Return items whose names appear in the answer
    items_mentioned = [
        r for r in items
        if r["item_name"].lower() in answer.lower()
    ][:6]

    return {"answer": answer, "items_mentioned": items_mentioned}