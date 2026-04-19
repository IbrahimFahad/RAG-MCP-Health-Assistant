"""
Drug-Drug Interaction Checker Service
Resolves drug names via NIH RxNav, then uses Claude AI to identify interactions.
RxNav's interaction endpoints are used for lookup only; Claude provides the analysis.
"""

import html as _html
import json
import requests
import anthropic
from app.config import ANTHROPIC_API_KEY

RXNAV_BASE = "https://rxnav.nlm.nih.gov/REST"

SEVERITY_CONFIG = {
    "high": {
        "color": "#ef4444", "bg": "#fef2f2", "border": "#fca5a5",
        "icon": "🚨", "label_en": "Serious", "label_ar": "خطير",
    },
    "moderate": {
        "color": "#f97316", "bg": "#fff7ed", "border": "#fdba74",
        "icon": "⚠️", "label_en": "Moderate", "label_ar": "متوسط",
    },
    "low": {
        "color": "#f59e0b", "bg": "#fffbeb", "border": "#fde68a",
        "icon": "💛", "label_en": "Minor", "label_ar": "طفيف",
    },
    "unknown": {
        "color": "#6b7280", "bg": "#f9fafb", "border": "#d1d5db",
        "icon": "ℹ️", "label_en": "Unknown", "label_ar": "غير محدد",
    },
}

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a clinical pharmacist expert. The user will provide a list of medication names.
Identify ALL known drug-drug interactions between them.

Respond ONLY with a valid JSON array (no markdown, no backticks). Each element:
{
  "drug1": "exact drug name",
  "drug2": "exact drug name",
  "severity": "high" | "moderate" | "low" | "unknown",
  "description": "Clear 1-2 sentence clinical explanation of the interaction and its risk."
}

Severity guide:
- high: life-threatening or requires immediate medical attention
- moderate: may worsen condition or require dose adjustment
- low: minor effect, usually manageable
- unknown: interaction reported but evidence is limited

If there are NO known interactions, respond with an empty array: []

Rules:
- Only include pairs from the provided drug list
- Be precise and clinically accurate
- Keep descriptions concise and practical
"""


def _get_rxcui(drug_name: str):
    """Resolve a drug name to its RxNorm concept ID. Returns None if not found."""
    try:
        resp = requests.get(
            f"{RXNAV_BASE}/rxcui.json",
            params={"name": drug_name.strip(), "search": 1},
            timeout=10,
        )
        resp.raise_for_status()
        ids = resp.json().get("idGroup", {}).get("rxnormId", [])
        return ids[0] if ids else None
    except requests.RequestException:
        raise
    except Exception:
        return None


def _normalize_severity(raw: str) -> str:
    raw = (raw or "").strip().lower()
    if raw in ("high", "serious", "major"):
        return "high"
    if raw in ("moderate", "medium"):
        return "moderate"
    if raw in ("low", "minor", "mild"):
        return "low"
    return "unknown"


def check_drug_interactions(drug_names: list, lang: str = "en") -> dict:
    """
    Check interactions between a list of medication names using Claude AI.

    Args:
        drug_names: list of 2–5 medication name strings
        lang: 'en' or 'ar'

    Returns dict with:
        success, drugs, interactions, has_serious, interaction_count, not_found, error
    """
    cleaned = [n.strip() for n in drug_names if n and n.strip()]

    if len(cleaned) < 2:
        return {
            "success": False,
            "error": (
                "Please enter at least 2 medications."
                if lang == "en" else
                "يرجى إدخال دواءين على الأقل."
            ),
        }

    # Try to resolve RxCUI for each drug (best-effort — used for display only)
    drugs = []
    for name in cleaned:
        try:
            rxcui = _get_rxcui(name)
        except Exception:
            rxcui = None
        drugs.append({"name": name, "rxcui": rxcui, "found": rxcui is not None})

    not_found = [d["name"] for d in drugs if not d["found"]]

    # Use Claude to check interactions — works regardless of RxNav API status
    drug_list_str = ", ".join(cleaned)
    user_msg = f"Check drug-drug interactions for: {drug_list_str}"

    try:
        response = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

        pairs = json.loads(raw)

    except json.JSONDecodeError:
        return {
            "success": False,
            "drugs": drugs,
            "error": (
                "Failed to parse interaction data. Please try again."
                if lang == "en" else
                "فشل تحليل بيانات التفاعلات. حاول مرة أخرى."
            ),
        }
    except Exception as e:
        return {
            "success": False,
            "drugs": drugs,
            "error": (
                f"Interaction check failed: {e}"
                if lang == "en" else
                f"فشل فحص التفاعلات: {e}"
            ),
        }

    # Build interaction list with styling config
    interactions = []
    order = {"high": 0, "moderate": 1, "low": 2, "unknown": 3}

    for pair in pairs:
        severity = _normalize_severity(pair.get("severity", ""))
        drug1 = _html.escape(str(pair.get("drug1", "")))
        drug2 = _html.escape(str(pair.get("drug2", "")))
        description = _html.escape(str(pair.get("description", "")))

        if drug1 and drug2 and description:
            interactions.append({
                "drug1": drug1,
                "drug2": drug2,
                "severity": severity,
                "description": description,
                **SEVERITY_CONFIG[severity],
            })

    interactions.sort(key=lambda x: order.get(x["severity"], 3))

    return {
        "success": True,
        "drugs": drugs,
        "interactions": interactions,
        "has_serious": any(i["severity"] == "high" for i in interactions),
        "interaction_count": len(interactions),
        "not_found": not_found,
    }
