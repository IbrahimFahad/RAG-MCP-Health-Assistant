"""
Food Nutrition Scanner Service
Analyzes food items and meals for nutritional content using Claude.
Supports Arabic and English input/output.
"""

import json
import anthropic
from app.config import ANTHROPIC_API_KEY
from app.mcp_tools.language_detector import detect_language
from app.mcp_tools.disclaimer_injector import inject_disclaimer
from app.mcp_tools.followup_generator import generate_followups


client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

NUTRITION_SYSTEM_PROMPT_EN = """You are a clinical nutrition expert. The user will describe a food item or meal.
Your job is to estimate the nutritional content as accurately as possible.

Respond ONLY with a valid JSON object (no markdown, no backticks, no extra text) with this exact structure:
{
  "food_name": "Name of the food/meal",
  "serving_size": "Estimated serving size (e.g., '1 cup, ~240g')",
  "calories": <number>,
  "macronutrients": {
    "protein_g": <number>,
    "carbs_g": <number>,
    "fat_g": <number>,
    "fiber_g": <number>,
    "sugar_g": <number>
  },
  "micronutrients": {
    "sodium_mg": <number>,
    "potassium_mg": <number>,
    "calcium_mg": <number>,
    "iron_mg": <number>,
    "vitamin_c_mg": <number>,
    "vitamin_a_iu": <number>
  },
  "health_notes": ["note1", "note2", "note3"],
  "category": "fruit|vegetable|grain|protein|dairy|fat|mixed_meal|beverage|snack|dessert|other"
}

Rules:
- Use standard USDA-style values when possible.
- If the food is a mixed meal, estimate totals for the full plate.
- If the description is vague, assume a typical adult serving.
- health_notes should contain 2-4 brief practical tips (allergy info, benefits, or cautions).
- All numeric values should be reasonable estimates, not zero unless truly negligible.
"""

NUTRITION_SYSTEM_PROMPT_AR = """أنت خبير تغذية سريرية. سيصف المستخدم طعامًا أو وجبة.
مهمتك هي تقدير المحتوى الغذائي بأكبر قدر ممكن من الدقة.

أجب فقط بكائن JSON صالح (بدون markdown، بدون backticks، بدون نص إضافي) بهذا الهيكل بالضبط:
{
  "food_name": "اسم الطعام/الوجبة بالعربية",
  "serving_size": "حجم الحصة المقدر",
  "calories": <رقم>,
  "macronutrients": {
    "protein_g": <رقم>,
    "carbs_g": <رقم>,
    "fat_g": <رقم>,
    "fiber_g": <رقم>,
    "sugar_g": <رقم>
  },
  "micronutrients": {
    "sodium_mg": <رقم>,
    "potassium_mg": <رقم>,
    "calcium_mg": <رقم>,
    "iron_mg": <رقم>,
    "vitamin_c_mg": <رقم>,
    "vitamin_a_iu": <رقم>
  },
  "health_notes": ["ملاحظة1", "ملاحظة2", "ملاحظة3"],
  "category": "fruit|vegetable|grain|protein|dairy|fat|mixed_meal|beverage|snack|dessert|other"
}

القواعد:
- استخدم قيم USDA القياسية عند الإمكان.
- إذا كان الطعام وجبة مختلطة، قدّر الإجمالي للطبق كاملاً.
- إذا كان الوصف غامضًا، افترض حصة بالغ عادية.
- health_notes يجب أن تحتوي على 2-4 نصائح عملية موجزة.
- جميع القيم الرقمية يجب أن تكون تقديرات معقولة.
"""


def scan_food(food_description: str) -> dict:
    """
    Analyze a food item or meal description and return nutritional data.

    Args:
        food_description: A text description of the food/meal (Arabic or English).

    Returns:
        dict with keys:
            - success (bool)
            - language (str): 'ar' or 'en'
            - nutrition (dict): parsed nutrition data (if success)
            - disclaimer (str): medical disclaimer
            - followups (list[str]): suggested follow-up questions
            - error (str): error message (if not success)
    """
    lang = detect_language(food_description)
    system_prompt = NUTRITION_SYSTEM_PROMPT_AR if lang == "ar" else NUTRITION_SYSTEM_PROMPT_EN

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": food_description}],
        )

        raw_text = response.content[0].text.strip()

        # Clean potential markdown fences
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[-1]
        if raw_text.endswith("```"):
            raw_text = raw_text.rsplit("```", 1)[0]
        raw_text = raw_text.strip()

        nutrition = json.loads(raw_text)

        disclaimer = inject_disclaimer(food_description, lang)
        followups = generate_followups(food_description, raw_text, lang)

        return {
            "success": True,
            "language": lang,
            "nutrition": nutrition,
            "disclaimer": disclaimer,
            "followups": followups,
        }

    except json.JSONDecodeError:
        return {
            "success": False,
            "language": lang,
            "error": "فشل تحليل البيانات الغذائية. حاول مرة أخرى." if lang == "ar"
                     else "Failed to parse nutritional data. Please try again.",
        }
    except Exception as e:
        return {
            "success": False,
            "language": lang,
            "error": f"حدث خطأ: {str(e)}" if lang == "ar" else f"An error occurred: {str(e)}",
        }


def get_category_emoji(category: str) -> str:
    """Return an emoji for the food category."""
    mapping = {
        "fruit": "🍎",
        "vegetable": "🥦",
        "grain": "🌾",
        "protein": "🥩",
        "dairy": "🧀",
        "fat": "🫒",
        "mixed_meal": "🍽️",
        "beverage": "🥤",
        "snack": "🍿",
        "dessert": "🍰",
        "other": "🍴",
    }
    return mapping.get(category, "🍴")


def get_calorie_level(calories: float) -> dict:
    """Classify calorie level for visual feedback."""
    if calories < 150:
        return {"label_en": "Low Calorie", "label_ar": "منخفض السعرات", "color": "#22c55e"}
    elif calories < 400:
        return {"label_en": "Moderate", "label_ar": "معتدل", "color": "#f59e0b"}
    elif calories < 700:
        return {"label_en": "High Calorie", "label_ar": "مرتفع السعرات", "color": "#f97316"}
    else:
        return {"label_en": "Very High", "label_ar": "مرتفع جداً", "color": "#ef4444"}
