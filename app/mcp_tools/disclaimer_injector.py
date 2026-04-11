DISCLAIMERS = {
    "general": {
        "en": "\n\n---\n> **Medical Disclaimer:** This information is for educational purposes only and does not constitute medical advice. Always consult a qualified healthcare professional for personal medical guidance.",
        "ar": "\n\n---\n> **إخلاء المسؤولية الطبية:** هذه المعلومات لأغراض تعليمية فقط ولا تُعدّ نصيحة طبية. استشر دائمًا طبيبًا مختصًا للحصول على إرشادات طبية شخصية.",
    },
    "medication": {
        "en": "\n\n---\n> **Medical Disclaimer:** Information about medications is for educational purposes only. **Never** start, stop, or change medication dosages without consulting your doctor or pharmacist. Incorrect use can be dangerous.",
        "ar": "\n\n---\n> **إخلاء المسؤولية الطبية:** المعلومات المتعلقة بالأدوية لأغراض تعليمية فقط. **لا تبدأ أو توقف أو تغير جرعات الدواء** دون استشارة طبيبك أو الصيدلاني. الاستخدام الخاطئ قد يكون خطيرًا.",
    },
    "emergency": {
        "en": "\n\n---\n> **⚠️ Medical Disclaimer:** If you or someone else is experiencing a medical emergency, **call emergency services (911 or your local number) immediately.** Do not rely on this information in an emergency situation.",
        "ar": "\n\n---\n> **⚠️ إخلاء المسؤولية الطبية:** إذا كنت أنت أو شخص آخر تعاني من حالة طوارئ طبية، **اتصل بالإسعاف فورًا.** لا تعتمد على هذه المعلومات في حالات الطوارئ.",
    },
    "mental_health": {
        "en": "\n\n---\n> **Medical Disclaimer:** Mental health information provided here is educational only. If you are struggling, please reach out to a licensed mental health professional or a crisis helpline.",
        "ar": "\n\n---\n> **إخلاء المسؤولية الطبية:** المعلومات المتعلقة بالصحة النفسية لأغراض تعليمية فقط. إذا كنت تعاني، يرجى التواصل مع متخصص نفسي مرخص أو خط مساعدة للأزمات.",
    },
}

# Keywords that trigger each disclaimer type
EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "stroke", "can't breathe", "unconscious",
    "overdose", "suicide", "severe bleeding", "seizure", "ألم في الصدر",
    "نوبة قلبية", "جرعة زائدة", "انتحار"
]

MEDICATION_KEYWORDS = [
    "dosage", "dose", "medication", "drug", "prescription", "antibiotic",
    "insulin", "metformin", "ibuprofen", "paracetamol", "aspirin",
    "جرعة", "دواء", "أدوية", "وصفة", "أنسولين", "مضاد حيوي"
]

MENTAL_HEALTH_KEYWORDS = [
    "depression", "anxiety", "mental health", "stress", "suicide",
    "panic attack", "bipolar", "schizophrenia", "اكتئاب", "قلق",
    "الصحة النفسية", "ضغط نفسي", "انتحار"
]


def detect_disclaimer_type(text: str) -> str:
    """Detect the appropriate disclaimer type based on content keywords."""
    text_lower = text.lower()

    for kw in EMERGENCY_KEYWORDS:
        if kw.lower() in text_lower:
            return "emergency"

    for kw in MEDICATION_KEYWORDS:
        if kw.lower() in text_lower:
            return "medication"

    for kw in MENTAL_HEALTH_KEYWORDS:
        if kw.lower() in text_lower:
            return "mental_health"

    return "general"


def inject_disclaimer(answer: str, language: str = "en", disclaimer_type: str = None) -> str:
    """
    Append the appropriate medical disclaimer to an answer.

    Args:
        answer:           The health answer text.
        language:         'en' or 'ar' — disclaimer will match the language.
        disclaimer_type:  Force a specific type, or auto-detect from content.

    Returns:
        Answer text with disclaimer appended.
    """
    if disclaimer_type is None:
        disclaimer_type = detect_disclaimer_type(answer)

    lang = language if language in ("en", "ar") else "en"
    disclaimer = DISCLAIMERS[disclaimer_type][lang]

    return answer + disclaimer
