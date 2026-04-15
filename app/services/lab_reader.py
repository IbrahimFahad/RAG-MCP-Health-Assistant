"""
Lab Results Reader service.
Extracts lab values from a PDF, compares to normal ranges,
and generates plain-language explanations using Claude.
"""
from dotenv import load_dotenv
load_dotenv(override=True)

import json
import anthropic
import fitz  # PyMuPDF
from app.config import ANTHROPIC_API_KEY

_client = None

def get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from uploaded PDF bytes."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = [page.get_text("text") for page in doc]
    doc.close()
    return "\n\n".join(p.strip() for p in pages if p.strip())


def analyze_lab_results(text: str, language: str = "en") -> dict:
    """
    Send extracted PDF text to Claude.
    Returns structured lab results with normal range comparison.
    """
    lang_instruction = (
        "Respond in Arabic (العربية)." if language == "ar"
        else "Respond in English."
    )

    prompt = f"""You are a medical lab results interpreter.

{lang_instruction}

Below is text extracted from a patient's lab report. Extract ALL lab test results and return them as a JSON object with this exact structure:

{{
  "patient_info": {{
    "name": "if found, else null",
    "date": "if found, else null"
  }},
  "results": [
    {{
      "test_name": "Test name in the language found",
      "value": "numeric value as string",
      "unit": "unit e.g. mg/dL",
      "normal_range": "e.g. 70-100",
      "normal_min": numeric_or_null,
      "normal_max": numeric_or_null,
      "status": "normal OR high OR low OR unknown",
      "explanation": "1-2 sentence plain language explanation of what this test measures and what the result means"
    }}
  ],
  "summary": "2-3 sentence overall summary of the results in plain language",
  "urgent": true_or_false
}}

If you cannot find lab values, return: {{"error": "No lab values found in this document."}}

Lab report text:
{text[:4000]}

Return only valid JSON, no extra text."""

    client = get_client()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()

    # Strip markdown code blocks if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "Could not parse lab results. Please make sure the PDF contains a blood test report."}


def get_status_color(status: str) -> str:
    return {
        "normal": "#22c55e",
        "high":   "#ef4444",
        "low":    "#3b82f6",
        "unknown": "#94a3b8",
    }.get(status.lower(), "#94a3b8")


def get_status_emoji(status: str) -> str:
    return {
        "normal":  "✅",
        "high":    "🔴",
        "low":     "🔵",
        "unknown": "⚪",
    }.get(status.lower(), "⚪")