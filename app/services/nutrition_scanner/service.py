"""
Nutrition Label Scanner Service
Extracts nutrition facts from food label images using Claude Vision API.
Stores scanned entries to Supabase for daily tracking.
Supports AI chat about the scanned label data.
"""

import json
import base64
import anthropic
from datetime import datetime, date
from typing import Optional
from supabase import create_client

from app.config import ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_KEY
from app.mcp_tools.disclaimer_injector import inject_disclaimer

# ---------- clients ----------
_claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
_supa = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------- constants ----------
NUTRITION_TABLE = "nutrition_log"

EXTRACTION_PROMPT_EN = """You are a nutrition label reader. Analyze this image of a food nutrition label.
Extract ALL nutritional information visible on the label and return ONLY a valid JSON object with this structure:
{
  "product_name": "string or null if not visible",
  "serving_size": "string or null",
  "servings_per_container": "string or null",
  "calories": number or null,
  "total_fat_g": number or null,
  "saturated_fat_g": number or null,
  "trans_fat_g": number or null,
  "cholesterol_mg": number or null,
  "sodium_mg": number or null,
  "total_carbohydrates_g": number or null,
  "dietary_fiber_g": number or null,
  "total_sugars_g": number or null,
  "added_sugars_g": number or null,
  "protein_g": number or null,
  "vitamin_d_mcg": number or null,
  "calcium_mg": number or null,
  "iron_mg": number or null,
  "potassium_mg": number or null
}

If a field is not visible on the label, set it to null.
If the label is in Arabic, still extract the values into the same JSON keys.
Return ONLY the JSON — no markdown, no explanation."""

EXTRACTION_PROMPT_AR = """أنت قارئ ملصقات غذائية. حلل هذه الصورة لملصق القيم الغذائية.
استخرج جميع المعلومات الغذائية الظاهرة على الملصق وأرجع فقط كائن JSON صالح بهذا الهيكل:
{
  "product_name": "اسم المنتج أو null إذا غير ظاهر",
  "serving_size": "حجم الحصة أو null",
  "servings_per_container": "عدد الحصص أو null",
  "calories": رقم أو null,
  "total_fat_g": رقم أو null,
  "saturated_fat_g": رقم أو null,
  "trans_fat_g": رقم أو null,
  "cholesterol_mg": رقم أو null,
  "sodium_mg": رقم أو null,
  "total_carbohydrates_g": رقم أو null,
  "dietary_fiber_g": رقم أو null,
  "total_sugars_g": رقم أو null,
  "added_sugars_g": رقم أو null,
  "protein_g": رقم أو null,
  "vitamin_d_mcg": رقم أو null,
  "calcium_mg": رقم أو null,
  "iron_mg": رقم أو null,
  "potassium_mg": رقم أو null
}

إذا لم يكن الحقل ظاهراً على الملصق، اجعله null.
أرجع فقط JSON — بدون markdown، بدون شرح."""

CHAT_SYSTEM_EN = """You are a friendly clinical nutrition assistant. The user has scanned a food nutrition label and you have been given the extracted data.
Answer their questions about the nutrition facts clearly and helpfully.
Give practical dietary advice based on the actual values from the label.
Always be concise and easy to understand. If the user asks something not related to the nutrition data, gently redirect them.
Never make a diagnosis. End responses with a brief disclaimer if giving health advice."""

CHAT_SYSTEM_AR = """أنت مساعد تغذية سريرية ودود. قام المستخدم بمسح ملصق قيم غذائية وتم تزويدك بالبيانات المستخرجة.
أجب على أسئلتهم حول القيم الغذائية بوضوح وبشكل مفيد.
قدم نصائح غذائية عملية بناءً على القيم الفعلية من الملصق.
كن دائماً موجزاً وسهل الفهم. إذا سأل المستخدم عن شيء غير متعلق بالبيانات الغذائية، أعد توجيهه بلطف.
لا تقدم تشخيصاً أبداً. أنهِ الردود بإخلاء مسؤولية موجز عند تقديم نصائح صحية."""


def _encode_image(image_bytes: bytes) -> str:
    """Base64-encode raw image bytes."""
    return base64.standard_b64encode(image_bytes).decode("utf-8")


def extract_nutrition(image_bytes: bytes, mime_type: str = "image/jpeg", language: str = "en") -> dict:
    """
    Send a nutrition label image to Claude Vision and extract structured data.

    Args:
        image_bytes: Raw bytes of the image.
        mime_type: MIME type of the image (image/jpeg, image/png, image/webp).
        language: 'en' or 'ar'.

    Returns:
        dict with nutrition fields, or {"error": "..."} on failure.
    """
    b64 = _encode_image(image_bytes)
    prompt = EXTRACTION_PROMPT_AR if language == "ar" else EXTRACTION_PROMPT_EN

    try:
        response = _claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": b64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            raw = raw.rsplit("```", 1)[0]
        data = json.loads(raw)
        return data
    except json.JSONDecodeError:
        return {"error": "Could not parse nutrition data from the image. Please try a clearer photo."}
    except Exception as e:
        return {"error": str(e)}


def chat_about_nutrition(
    question: str,
    nutrition_context: dict,
    history: list[dict],
    language: str = "en",
) -> str:
    """
    Answer a user question about a scanned nutrition label.

    Args:
        question: The user's question.
        nutrition_context: The extracted nutrition dict from the label scan.
        history: List of {"role": "user"/"assistant", "content": "..."} prior messages.
        language: 'en' or 'ar'.

    Returns:
        AI answer string, or an error message string.
    """
    system = CHAT_SYSTEM_AR if language == "ar" else CHAT_SYSTEM_EN

    # Build context summary to prepend to the first user message
    context_summary = f"Nutrition label data:\n{json.dumps(nutrition_context, ensure_ascii=False, indent=2)}"

    # Build messages list: inject context into the very first user turn
    messages = []
    for i, msg in enumerate(history):
        if i == 0 and msg["role"] == "user":
            messages.append({"role": "user", "content": f"{context_summary}\n\nUser question: {msg['content']}"})
        else:
            messages.append(msg)

    # Add the current question
    if not history:
        messages.append({"role": "user", "content": f"{context_summary}\n\nUser question: {question}"})
    else:
        messages.append({"role": "user", "content": question})

    try:
        response = _claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system,
            messages=messages,
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"


def save_nutrition_entry(nutrition: dict, language: str = "en", notes: str = "") -> dict:
    """
    Persist a scanned nutrition entry to Supabase.

    Returns:
        {"success": True, "id": ...} or {"success": False, "error": ...}
    """
    row = {
        "product_name": nutrition.get("product_name"),
        "serving_size": nutrition.get("serving_size"),
        "servings_per_container": nutrition.get("servings_per_container"),
        "calories": nutrition.get("calories"),
        "total_fat_g": nutrition.get("total_fat_g"),
        "saturated_fat_g": nutrition.get("saturated_fat_g"),
        "trans_fat_g": nutrition.get("trans_fat_g"),
        "cholesterol_mg": nutrition.get("cholesterol_mg"),
        "sodium_mg": nutrition.get("sodium_mg"),
        "total_carbohydrates_g": nutrition.get("total_carbohydrates_g"),
        "dietary_fiber_g": nutrition.get("dietary_fiber_g"),
        "total_sugars_g": nutrition.get("total_sugars_g"),
        "added_sugars_g": nutrition.get("added_sugars_g"),
        "protein_g": nutrition.get("protein_g"),
        "vitamin_d_mcg": nutrition.get("vitamin_d_mcg"),
        "calcium_mg": nutrition.get("calcium_mg"),
        "iron_mg": nutrition.get("iron_mg"),
        "potassium_mg": nutrition.get("potassium_mg"),
        "language": language,
        "notes": notes,
        "scanned_at": datetime.utcnow().isoformat(),
    }
    try:
        result = _supa.table(NUTRITION_TABLE).insert(row).execute()
        return {"success": True, "id": result.data[0]["id"] if result.data else None}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_daily_log(target_date: Optional[date] = None) -> list[dict]:
    """
    Fetch all nutrition entries for a given date (defaults to today).
    """
    if target_date is None:
        target_date = date.today()

    start = f"{target_date.isoformat()}T00:00:00"
    end = f"{target_date.isoformat()}T23:59:59"

    try:
        result = (
            _supa.table(NUTRITION_TABLE)
            .select("*")
            .gte("scanned_at", start)
            .lte("scanned_at", end)
            .order("scanned_at", desc=False)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def compute_daily_totals(entries: list[dict]) -> dict:
    """
    Sum key nutritional values across a list of entries.
    """
    keys = [
        "calories", "total_fat_g", "saturated_fat_g", "trans_fat_g",
        "cholesterol_mg", "sodium_mg", "total_carbohydrates_g",
        "dietary_fiber_g", "total_sugars_g", "added_sugars_g",
        "protein_g", "vitamin_d_mcg", "calcium_mg", "iron_mg", "potassium_mg",
    ]
    totals = {}
    for k in keys:
        vals = [e.get(k) for e in entries if e.get(k) is not None]
        totals[k] = round(sum(vals), 1) if vals else 0
    return totals