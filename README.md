# Agentic RAG Health Assistant

A bilingual (Arabic + English) health question-answering system powered by Claude AI, Supabase vector search, and MCP tools.

## What It Does

- User asks a health question in Arabic or English
- System searches a vector database first
- If found (similarity > 0.75) → answers instantly from DB
- If not found → searches the web, scrapes trusted sources, stores results, then answers
- Next time the same question is asked → answered from DB instantly

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Claude Sonnet (Anthropic API) |
| Vector DB | Supabase pgvector |
| Embeddings | multilingual-e5-large (HuggingFace) |
| Web Search | Tavily API |
| Web Scraping | BeautifulSoup / Firecrawl |
| Medical Literature | PubMed NIH API |
| Backend | Python + FastAPI |
| Frontend | Streamlit |

## Project Structure

```
RAG-MCP/
├── app/
│   ├── agent/          # Agent loop, tool executor, RAG pipeline
│   ├── embeddings/     # Embedding model, chunker, document loader
│   ├── mcp_tools/      # All MCP tools (search, scraper, calculators...)
│   ├── retrieval/      # Supabase vector search and storage
│   └── config.py       # Environment variables
├── frontend/
│   └── app.py          # Streamlit chat UI
├── scripts/
│   ├── seed_database.py    # Pre-populate DB with health documents
│   └── test_supabase.py    # Test DB connection
├── tests/
│   └── test_pipeline.py    # Full pipeline tests
├── data/
│   ├── raw/            # Original documents
│   └── processed/      # Processed chunks
├── .env                # API keys (not committed)
└── requirements.txt
```

## Setup

### 1. Clone and install dependencies

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows
source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 2. Configure API keys

Copy `.env.example` to `.env` and fill in:

```
ANTHROPIC_API_KEY=your_key
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
TAVILY_API_KEY=your_key
```

### 3. Set up Supabase

Run in Supabase SQL Editor:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE health_knowledge (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1024),
    language VARCHAR(10),
    source_url TEXT,
    source_type VARCHAR(50),
    title TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ON health_knowledge
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE OR REPLACE FUNCTION search_health_knowledge(
    query_embedding VECTOR(1024),
    match_threshold FLOAT DEFAULT 0.75,
    match_count INT DEFAULT 3
)
RETURNS TABLE (id BIGINT, content TEXT, language VARCHAR(10),
               source_url TEXT, source_type VARCHAR(50),
               title TEXT, metadata JSONB, similarity FLOAT)
LANGUAGE SQL STABLE AS $$
    SELECT id, content, language, source_url, source_type, title, metadata,
           1 - (embedding <=> query_embedding) AS similarity
    FROM health_knowledge
    WHERE 1 - (embedding <=> query_embedding) > match_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;
```

### 4. Seed the database

```bash
python scripts/seed_database.py
```

### 5. Run the app

```bash
python -m streamlit run frontend/app.py
```

Open http://localhost:8501

## MCP Tools

| Tool | Description |
|---|---|
| web_search | Tavily web search for health info |
| scrape_url | Extract content from medical websites |
| pubmed_search | Search NIH PubMed for clinical studies |
| store_to_db | Save new knowledge to vector DB |
| calculate_bmi | BMI calculator with WHO classification |
| calculate_bmr | Daily calorie needs calculator |
| calculate_ideal_weight | Ideal body weight (Devine formula) |

## Arabic Support

- multilingual-e5-large embeds Arabic and English in the same vector space
- Arabic query can match English documents and vice versa
- Claude responds in the same language the user writes in
- RTL layout in the frontend for Arabic text
