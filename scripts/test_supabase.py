from dotenv import load_dotenv
load_dotenv()

from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY

def test_connection():
    print("Testing Supabase connection...")
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Client created.")

    print("\nChecking health_knowledge table exists...")
    result = client.table("health_knowledge").select("id").limit(1).execute()
    print(f"Table accessible. Rows returned: {len(result.data)}")

    print("\nInserting a test row...")
    dummy_embedding = [0.0] * 1024
    insert_result = client.table("health_knowledge").insert({
        "content": "Test: Drinking water is important for health.",
        "embedding": dummy_embedding,
        "language": "en",
        "source_type": "manual",
        "title": "Test Entry"
    }).execute()
    inserted_id = insert_result.data[0]["id"]
    print(f"Inserted row with id: {inserted_id}")

    print("\nReading it back...")
    read_result = client.table("health_knowledge").select("id, content, language").eq("id", inserted_id).execute()
    print(f"Read back: {read_result.data[0]}")

    print("\nDeleting test row...")
    client.table("health_knowledge").delete().eq("id", inserted_id).execute()
    print("Test row deleted.")

    print("\nAll tests passed! Supabase is ready.")

if __name__ == "__main__":
    test_connection()
