import json
import anthropic
from app.config import ANTHROPIC_API_KEY

TRIAGE_CONFIG = {
    "emergency": {
        "color": "#ef4444", "bg": "#fef2f2", "border": "#fca5a5",
        "icon": "🚨",
        "label_en": "Emergency", "label_ar": "طوارئ",
        "advice_en": "Call emergency services (911/920) immediately.",
        "advice_ar": "اتصل بالطوارئ فوراً (911/920).",
    },
    "consultation_24": {
        "color": "#f97316", "bg": "#fff7ed", "border": "#fdba74",
        "icon": "⚠️",
        "label_en": "See a Doctor Within 24 Hours", "label_ar": "زر طبيباً خلال 24 ساعة",
        "advice_en": "Your symptoms need medical evaluation within 24 hours.",
        "advice_ar": "تستدعي أعراضك تقييماً طبياً خلال 24 ساعة.",
    },
    "consultation": {
        "color": "#f59e0b", "bg": "#fffbeb", "border": "#fde68a",
        "icon": "📅",
        "label_en": "Schedule a Doctor Visit", "label_ar": "احجز موعداً مع الطبيب",
        "advice_en": "Schedule an appointment with your doctor soon.",
        "advice_ar": "احجز موعداً مع طبيبك في أقرب وقت.",
    },
    "self_care": {
        "color": "#10b981", "bg": "#e8f5f0", "border": "#6ee7b7",
        "icon": "🏠",
        "label_en": "Self-Care at Home", "label_ar": "رعاية ذاتية في المنزل",
        "advice_en": "Your symptoms can likely be managed at home. Monitor for any worsening.",
        "advice_ar": "يمكن على الأرجح إدارة أعراضك في المنزل. راقب أي تدهور في حالتك.",
    },
}

SYSTEM_PROMPT = """You are an experienced clinical physician assistant. The user will describe their symptoms, age, and sex.

Analyze the symptoms and respond ONLY with a valid JSON object (no markdown, no backticks). Format:

{
  "triage_level": "emergency" | "consultation_24" | "consultation" | "self_care",
  "conditions": [
    {
      "name": "Condition name in English",
      "probability": 0.82,
      "severity": "mild" | "moderate" | "severe",
      "icd10_code": "J06.9"
    }
  ],
  "explanation": "Clear, empathetic 2-3 sentence plain-language summary of findings.",
  "red_flags": ["symptom1", "symptom2"]
}

Rules:
- List 3 to 6 most likely conditions, ordered by probability (highest first)
- probability is a float between 0.0 and 1.0
- triage_level must be one of the four exact strings above
- explanation must match the language of the input (Arabic if user wrote in Arabic, English otherwise)
- red_flags: list any symptoms that warrant urgent attention; empty list if none
- Be clinically accurate but explain in plain language
- icd10_code is optional — include only if confident
- Never invent symptoms the user did not mention"""

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def check_symptoms(symptoms_text: str, age: int, sex: str, lang: str = "en") -> dict:
    """
    Analyze symptoms using Claude AI and return differential diagnosis + triage.

    Args:
        symptoms_text: Natural language description of symptoms
        age: Patient age in years
        sex: 'male' or 'female'
        lang: 'en' or 'ar'

    Returns dict with keys:
        success, conditions, triage_level, triage_config, explanation, red_flags, error
    """
    if not symptoms_text or not symptoms_text.strip():
        return {
            "success": False,
            "error": (
                "Please describe your symptoms."
                if lang == "en" else
                "يرجى وصف أعراضك."
            ),
        }

    if not (1 <= age <= 130):
        return {
            "success": False,
            "error": (
                "Please enter a valid age (1–130)."
                if lang == "en" else
                "يرجى إدخال عمر صحيح (1–130)."
            ),
        }

    user_message = (
        f"Patient: {age}-year-old {sex}\n"
        f"Symptoms: {symptoms_text.strip()}"
    )

    try:
        response = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = response.content[0].text.strip()

        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

        data = json.loads(raw)

    except json.JSONDecodeError:
        return {
            "success": False,
            "error": (
                "Failed to parse the analysis. Please try again."
                if lang == "en" else
                "فشل تحليل النتائج. حاول مرة أخرى."
            ),
        }
    except Exception as e:
        return {
            "success": False,
            "error": (
                f"Analysis failed: {e}"
                if lang == "en" else
                f"فشل التحليل: {e}"
            ),
        }

    triage_level = data.get("triage_level", "consultation")
    if triage_level not in TRIAGE_CONFIG:
        triage_level = "consultation"

    conditions = []
    for c in data.get("conditions", [])[:6]:
        prob = float(c.get("probability", 0))
        conditions.append({
            "name": str(c.get("name", "")),
            "probability": max(0.0, min(1.0, prob)),
            "severity": str(c.get("severity", "")),
            "icd10_code": str(c.get("icd10_code", "")),
        })

    return {
        "success": True,
        "conditions": conditions,
        "triage_level": triage_level,
        "triage_config": TRIAGE_CONFIG[triage_level],
        "explanation": str(data.get("explanation", "")),
        "red_flags": data.get("red_flags", []),
    }
