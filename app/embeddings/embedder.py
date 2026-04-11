from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL

# Load model once at module level — reused across all calls
# First run downloads ~1.1GB from HuggingFace, then cached locally
_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print("Model loaded.")
    return _model

def embed(text: str) -> list[float]:
    """
    Embed a single text string.
    multilingual-e5-large expects a prefix:
      - 'query: ' for search queries
      - 'passage: ' for documents being stored
    We use 'query: ' here as a general default.
    """
    model = get_model()
    vector = model.encode(f"query: {text}", normalize_embeddings=True)
    return vector.tolist()

def embed_query(text: str) -> list[float]:
    """Embed a user search query."""
    model = get_model()
    vector = model.encode(f"query: {text}", normalize_embeddings=True)
    return vector.tolist()

def embed_passage(text: str) -> list[float]:
    """Embed a document/passage to be stored in the DB."""
    model = get_model()
    vector = model.encode(f"passage: {text}", normalize_embeddings=True)
    return vector.tolist()
