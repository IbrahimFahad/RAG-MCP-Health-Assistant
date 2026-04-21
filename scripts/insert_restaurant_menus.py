"""
One-time script: insert all Saudi restaurant menu data into the restaurant_menu table.
Run from project root: python scripts/insert_restaurant_menus.py

Make sure you have already run scripts/restaurant_menu_table.sql in Supabase first.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(override=True)

from app.services.restaurant_nutrition.data import RESTAURANTS
from app.retrieval.store import get_client


def insert_all():
    client = get_client()

    rows = []
    for key, rest in RESTAURANTS.items():
        for item in rest["items"]:
            rows.append({
                "restaurant_key":  key,
                "restaurant_name": rest["name_en"],
                "restaurant_ar":   rest["name_ar"],
                "restaurant_cat":  rest["category"],
                "restaurant_emoji":rest["emoji"],
                "item_name":       item["name_en"],
                "item_name_ar":    item["name_ar"],
                "item_category":   item["category"],
                "calories":        item["calories"],
                "protein_g":       item["protein_g"],
                "carbs_g":         item["carbs_g"],
                "fat_g":           item["fat_g"],
                "sodium_mg":       item["sodium_mg"],
                "fiber_g":         item["fiber_g"],
            })

    print(f"Inserting {len(rows)} menu items into restaurant_menu table...")
    # Insert in batches of 50
    batch_size = 50
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        client.table("restaurant_menu").insert(batch).execute()
        print(f"  Inserted rows {i+1} - {min(i+batch_size, len(rows))}")

    print(f"Done! {len(rows)} items inserted.")


if __name__ == "__main__":
    insert_all()