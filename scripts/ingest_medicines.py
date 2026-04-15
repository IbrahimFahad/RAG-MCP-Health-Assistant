"""
Ingest medicine data into the medicine_knowledge table.

Usage:
    python scripts/ingest_medicines.py

What it ingests (in order):
  1. Medicine_Details.csv  — best structured dataset (11k medicines)
  2. Any .pdf or .txt files in data/medicines/

Skips medicine_dataset*.csv files (synthetic/incomplete data).

IMPORTANT: Run scripts/medicine_table.sql in Supabase first.
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(override=True)

from app.services.medicine_db import store_medicine_chunks

MEDICINES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "medicines")

# How many CSV rows to ingest (None = all rows)
# For a demo: 500 is fast (~5 min). For production: set to None.
CSV_LIMIT = None


def row_to_text(row: dict) -> tuple[str, str]:
    """
    Convert a Medicine_Details.csv row to (title, text_passage).
    Returns ("", "") if the row has no useful data.
    """
    name        = row.get("Medicine Name", "").strip()
    composition = row.get("Composition", "").strip()
    uses        = row.get("Uses", "").strip()
    side_effects= row.get("Side_effects", "").strip()
    manufacturer= row.get("Manufacturer", "").strip()

    if not name:
        return "", ""

    parts = [f"Medicine: {name}"]
    if composition:
        parts.append(f"Composition: {composition}")
    if uses:
        parts.append(f"Uses / Indications: {uses}")
    if side_effects:
        parts.append(f"Side effects: {side_effects}")
    if manufacturer:
        parts.append(f"Manufacturer: {manufacturer}")

    return name, "\n".join(parts)


def ingest_csv(filepath: str, limit: int = None):
    print(f"\n{'='*60}")
    print(f"Ingesting CSV: {os.path.basename(filepath)}")
    if limit:
        print(f"Row limit: {limit}")
    print(f"{'='*60}")

    total   = 0
    skipped = 0
    chunks_total = 0

    with open(filepath, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break

            title, text = row_to_text(row)
            if not text:
                skipped += 1
                continue

            try:
                n = store_medicine_chunks(text, title=title)
                chunks_total += n
                total += 1
                if total % 50 == 0:
                    print(f"  {total} medicines ingested ({chunks_total} chunks)...")
            except Exception as e:
                print(f"  WARN row {i}: {e}")
                skipped += 1

    print(f"Done. {total} medicines ingested, {chunks_total} chunks stored, {skipped} skipped.")
    return total


def ingest_pdf_or_txt(filepath: str):
    name = os.path.splitext(os.path.basename(filepath))[0].replace("_", " ").replace("-", " ").title()
    print(f"  Ingesting file: {os.path.basename(filepath)} -> '{name}' ...", end=" ", flush=True)

    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".pdf":
            import fitz
            doc  = fitz.open(filepath)
            text = "\n\n".join(p.get_text("text").strip() for p in doc if p.get_text("text").strip())
            doc.close()
        else:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        if not text.strip():
            print("SKIP (empty)")
            return

        n = store_medicine_chunks(text, title=name)
        print(f"OK ({n} chunks)")
    except Exception as e:
        print(f"FAILED: {e}")


def main():
    print("Medicine Knowledge Ingestion")
    print("="*60)

    # ── 1. Best CSV dataset ───────────────────────────────────────
    csv_path = os.path.join(MEDICINES_DIR, "Medicine_Details.csv")
    if os.path.exists(csv_path):
        ingest_csv(csv_path, limit=CSV_LIMIT)
    else:
        print(f"WARNING: Medicine_Details.csv not found in {MEDICINES_DIR}")

    # ── 2. Any PDFs or TXTs ───────────────────────────────────────
    other_files = [
        f for f in os.listdir(MEDICINES_DIR)
        if f.lower().endswith((".pdf", ".txt"))
    ]
    if other_files:
        print(f"\nIngesting {len(other_files)} PDF/TXT file(s)...")
        for filename in sorted(other_files):
            ingest_pdf_or_txt(os.path.join(MEDICINES_DIR, filename))

    print("\n" + "="*60)
    print("All done. Medicines are now in the medicine_knowledge table.")
    print("Users can now ask medicine questions in the app.")


if __name__ == "__main__":
    main()