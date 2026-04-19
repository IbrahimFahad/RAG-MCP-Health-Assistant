"""
One-time script: ingest all Saudi restaurant menu data into Supabase RAG vector store.
Run from project root: python scripts/ingest_restaurant_menus.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(override=True)

from app.services.restaurant_nutrition.data import RESTAURANTS
from app.embeddings.embedder import embed_passage
from app.retrieval.store import get_client

BATCH_SIZE = 10


def build_chunks() -> list[dict]:
    chunks = []

    for key, rest in RESTAURANTS.items():
        # --- Restaurant summary chunk ---
        item_names = ", ".join(i["name_en"] for i in rest["items"][:8])
        summary = (
            f"Restaurant: {rest['name_en']} ({rest['name_ar']}) — {rest['category']} in Saudi Arabia. "
            f"Popular items include: {item_names}. "
            f"Total {len(rest['items'])} menu items available with full nutrition data."
        )
        chunks.append({
            "text": summary,
            "title": f"{rest['name_en']} Menu Summary",
            "restaurant": rest["name_en"],
            "restaurant_ar": rest["name_ar"],
            "item_name": None,
            "category": "summary",
        })

        # --- One chunk per item ---
        for item in rest["items"]:
            text = (
                f"Restaurant: {rest['name_en']} ({rest['name_ar']}) | "
                f"Item: {item['name_en']} ({item['name_ar']}) | "
                f"Category: {item['category']} | "
                f"Calories: {item['calories']} kcal | "
                f"Protein: {item['protein_g']}g | "
                f"Carbohydrates: {item['carbs_g']}g | "
                f"Fat: {item['fat_g']}g | "
                f"Sodium: {item['sodium_mg']}mg | "
                f"Fiber: {item['fiber_g']}g"
            )
            chunks.append({
                "text": text,
                "title": f"{rest['name_en']} - {item['name_en']}",
                "restaurant": rest["name_en"],
                "restaurant_ar": rest["name_ar"],
                "item_name": item["name_en"],
                "category": item["category"],
            })

    return chunks


def ingest():
    chunks = build_chunks()
    print(f"Total chunks to ingest: {len(chunks)}")
    client = get_client()

    for i, chunk in enumerate(chunks):
        print(f"  [{i+1}/{len(chunks)}] Embedding: {chunk['title'][:60]}...")
        embedding = embed_passage(chunk["text"])
        row = {
            "content":     chunk["text"],
            "embedding":   embedding,
            "source_url":  f"restaurant://{chunk['restaurant'].lower().replace(' ', '_')}",
            "title":       chunk["title"],
            "language":    "en",
            "source_type": "restaurant",
            "metadata":    {
                "restaurant":    chunk["restaurant"],
                "restaurant_ar": chunk["restaurant_ar"],
                "item_name":     chunk["item_name"],
                "category":      chunk["category"],
            },
        }
        result = client.table("health_knowledge").insert(row).execute()
        print(f"     Stored -> id: {result.data[0]['id']}")

    print(f"\n✅ Done! Ingested {len(chunks)} restaurant menu chunks into Supabase.")


if __name__ == "__main__":
    ingest()