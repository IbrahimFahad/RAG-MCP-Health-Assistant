import re
from langdetect import detect, LangDetectException

# Arabic Unicode range: \u0600-\u06FF
ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF]')


def detect_language(text: str) -> str:
    """
    Detect whether text is Arabic ('ar') or English ('en').

    Strategy:
        1. If text has Arabic characters -> 'ar' (fast, reliable)
        2. Otherwise use langdetect library
        3. If langdetect fails or returns unexpected -> default to 'en'

    Returns:
        'ar' or 'en'
    """
    if not text or not text.strip():
        return "en"

    # Check for Arabic characters directly — most reliable for short texts
    arabic_chars = len(ARABIC_PATTERN.findall(text))
    total_chars = len(text.replace(" ", ""))

    if total_chars > 0 and arabic_chars / total_chars > 0.2:
        return "ar"

    # Use langdetect for everything else
    try:
        lang = detect(text)
        # Map langdetect codes to our two supported languages
        if lang == "ar":
            return "ar"
        return "en"
    except LangDetectException:
        return "en"


def is_arabic(text: str) -> bool:
    return detect_language(text) == "ar"


def is_english(text: str) -> bool:
    return detect_language(text) == "en"
