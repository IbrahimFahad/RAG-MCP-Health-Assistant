from dotenv import load_dotenv
import os

load_dotenv(override=True)

# Claude API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Web Search
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Web Scraping
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# Azure OCR (optional)
AZURE_DOC_INTEL_ENDPOINT = os.getenv("AZURE_DOC_INTEL_ENDPOINT")
AZURE_DOC_INTEL_KEY = os.getenv("AZURE_DOC_INTEL_KEY")

# App Settings
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.75))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 3))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
