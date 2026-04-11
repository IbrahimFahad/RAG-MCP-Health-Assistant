from dotenv import load_dotenv
load_dotenv(override=True)

import anthropic
from app.config import ANTHROPIC_API_KEY

_client = None

def get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def generate_followups(question: str, answer: str, language: str = "en") -> list[str]:
    """
    Generate 3 relevant follow-up questions based on the original question and answer.

    Args:
        question: The original user question.
        answer:   The answer the system gave.
        language: 'en' or 'ar' — follow-ups will be in the same language.

    Returns:
        List of 3 follow-up question strings.
    """
    if language == "ar":
        prompt = f"""بناءً على السؤال والإجابة التالية، اقترح 3 أسئلة متابعة مفيدة قد يريد المستخدم طرحها.

السؤال الأصلي: {question}

الإجابة: {answer[:500]}

اكتب فقط 3 أسئلة، كل سؤال في سطر منفصل، بدون ترقيم أو تنسيق إضافي."""
    else:
        prompt = f"""Based on the following health question and answer, suggest 3 useful follow-up questions the user might want to ask next.

Original question: {question}

Answer: {answer[:500]}

Write only 3 questions, one per line, with no numbering or extra formatting."""

    try:
        client = get_client()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        questions = [q.strip() for q in raw.splitlines() if q.strip()]
        return questions[:3]
    except Exception:
        # Fallback: return generic follow-ups if API is unavailable
        if language == "ar":
            return [
                f"ما هي أعراض هذه الحالة؟",
                f"كيف يتم علاج هذه الحالة؟",
                f"كيف يمكن الوقاية من هذه الحالة؟",
            ]
        return [
            f"What are the symptoms of this condition?",
            f"What are the treatment options available?",
            f"How can this condition be prevented?",
        ]
