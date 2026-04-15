"""
Fetch Patient Information Leaflet (PIL) data from free APIs and store in medicine_knowledge.

Sources used (in order):
  1. DailyMed (US NLM)  — full structured drug labels
  2. OpenFDA drug label  — indications, dosage, warnings, side effects
  3. NHS Medicines API   — plain-language UK patient info

Usage:
    python scripts/fetch_pil.py                     # all medicines in MEDICINES list
    python scripts/fetch_pil.py "PANADOL"           # single medicine
    python scripts/fetch_pil.py "PANADOL" "ASPIRIN" # multiple
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(override=True)

import requests
from app.services.medicine_db import store_medicine_chunks

# ── Default medicine list ─────────────────────────────────────────────────────
MEDICINES = [
    "Panadol", "Paracetamol", "Ibuprofen", "Aspirin", "Amoxicillin",
    "Metformin", "Omeprazole", "Atorvastatin", "Lisinopril", "Amlodipine",
    "Cetirizine", "Loratadine", "Azithromycin", "Ciprofloxacin", "Metronidazole",
    "Prednisolone", "Dexamethasone", "Salbutamol", "Warfarin", "Clopidogrel",
    "Diclofenac", "Naproxen", "Codeine", "Tramadol", "Morphine",
    "Insulin", "Levothyroxine", "Sertraline", "Fluoxetine", "Amitriptyline",
]

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "MediAssist-CollegeProject/1.0"})


# ── DailyMed ──────────────────────────────────────────────────────────────────

def fetch_dailymed(medicine_name: str) -> str | None:
    """Fetch full drug label text from DailyMed (US NLM)."""
    try:
        # Step 1: find the SPL set ID
        search_url = (
            f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json"
            f"?drug_name={requests.utils.quote(medicine_name)}&pagesize=1"
        )
        r = SESSION.get(search_url, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json().get("data", [])
        if not data:
            return None

        set_id = data[0].get("setid")
        if not set_id:
            return None

        # Step 2: fetch the full label
        label_url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{set_id}.json"
        r2 = SESSION.get(label_url, timeout=10)
        if r2.status_code != 200:
            return None

        label = r2.json().get("data", {})
        title = label.get("title", medicine_name)

        # Extract sections
        sections = label.get("sections", [])
        parts = [f"Medicine: {title} (Source: DailyMed)"]
        for section in sections:
            name = section.get("name", "").strip()
            text = section.get("text", "").strip()
            if name and text and len(text) > 20:
                parts.append(f"\n{name.upper()}:\n{text[:1000]}")

        return "\n".join(parts) if len(parts) > 1 else None

    except Exception as e:
        return None


# ── OpenFDA ───────────────────────────────────────────────────────────────────

def fetch_openfda(medicine_name: str) -> str | None:
    """Fetch drug label from OpenFDA."""
    def _try(field):
        url = (
            f"https://api.fda.gov/drug/label.json"
            f"?search=openfda.{field}:\"{medicine_name}\"&limit=1"
        )
        try:
            r = SESSION.get(url, timeout=8)
            if r.status_code == 200:
                results = r.json().get("results")
                if results:
                    return results[0]
        except Exception:
            pass
        return None

    label = _try("brand_name") or _try("generic_name")
    if not label:
        # Full text search
        try:
            url = f"https://api.fda.gov/drug/label.json?search=\"{medicine_name}\"&limit=1"
            r = SESSION.get(url, timeout=8)
            if r.status_code == 200:
                results = r.json().get("results", [])
                if results:
                    label = results[0]
        except Exception:
            pass

    if not label:
        return None

    def _get(obj, *keys):
        for k in keys:
            v = obj.get(k)
            if v:
                return (" ".join(v) if isinstance(v, list) else str(v))[:1000]
        return ""

    openfda = label.get("openfda", {})
    brand   = _get(openfda, "brand_name")
    generic = _get(openfda, "generic_name")
    name    = brand or generic or medicine_name

    parts = [f"Medicine: {name} (Source: FDA Drug Label)"]
    if generic and generic != name:
        parts.append(f"Generic name: {generic}")

    for heading, *keys in [
        ("INDICATIONS AND USAGE",         "indications_and_usage"),
        ("DOSAGE AND ADMINISTRATION",     "dosage_and_administration"),
        ("WARNINGS",                       "warnings", "warnings_and_cautions", "boxed_warning"),
        ("ADVERSE REACTIONS / SIDE EFFECTS", "adverse_reactions"),
        ("CONTRAINDICATIONS",             "contraindications"),
        ("DRUG INTERACTIONS",             "drug_interactions"),
        ("HOW SUPPLIED",                  "how_supplied"),
        ("DESCRIPTION",                   "description"),
    ]:
        text = _get(label, *keys)
        if text:
            parts.append(f"\n{heading}:\n{text}")

    return "\n".join(parts) if len(parts) > 1 else None


# ── NHS Medicines ─────────────────────────────────────────────────────────────

def fetch_nhs(medicine_name: str) -> str | None:
    """Fetch plain-language info from NHS Medicines API."""
    try:
        url = (
            f"https://api.nhs.uk/medicines/"
            f"?term={requests.utils.quote(medicine_name)}"
        )
        # NHS API sometimes needs a key; try without first
        r = SESSION.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            items = data.get("significantLink", []) or data.get("hasPart", [])
            if items:
                item = items[0]
                desc = item.get("description", "")
                name = item.get("name", medicine_name)
                if desc:
                    return f"Medicine: {name} (Source: NHS Medicines)\n\n{desc[:2000]}"
    except Exception:
        pass
    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def fetch_and_store(medicine_name: str) -> bool:
    """Try all sources for a medicine and store the best result."""
    print(f"\n  [{medicine_name}]")

    # Try sources in order — store the first one that returns data
    for source_name, fetch_fn in [
        ("DailyMed", fetch_dailymed),
        ("OpenFDA",  fetch_openfda),
        ("NHS",      fetch_nhs),
    ]:
        text = fetch_fn(medicine_name)
        if text and len(text.strip()) > 100:
            title = f"{medicine_name} PIL"
            n = store_medicine_chunks(text, title=title, source_url=f"PIL:{source_name}")
            print(f"    OK {source_name} -> {n} chunk(s) stored")
            return True
        else:
            print(f"    - {source_name}: not found")

    print(f"    MISS No PIL data found for {medicine_name}")
    return False


def main():
    names = sys.argv[1:] if len(sys.argv) > 1 else MEDICINES

    print(f"Fetching PIL data for {len(names)} medicine(s)...")
    print("="*60)

    ok = 0
    for name in names:
        if fetch_and_store(name):
            ok += 1
        time.sleep(0.3)  # be polite to APIs

    print("\n" + "="*60)
    print(f"Done. {ok}/{len(names)} medicines stored in medicine_knowledge.")

if __name__ == "__main__":
    main()