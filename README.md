# 🏥 MediAssist — AI Health Platform

A bilingual **(Arabic + English)** AI health assistant built as a college project. Powered by Claude AI (Anthropic) and Supabase.

---

## ✨ Features — 8 AI Services

| Service | Description |
|---|---|
| 🩺 Health Q&A | Ask any health question — AI answers using RAG + trusted medical sources |
| ⚖️ Health Calculators | BMI, daily calorie needs, ideal body weight |
| 🩸 Lab Results Reader | Upload blood test PDF → plain-language explanation of every value |
| 🚑 Emergency Triage | Guided yes/no symptom checker → care urgency level |
| 💊 Medicine Info | Ask about dosage, side effects, and drug interactions |
| 🥗 Food Nutrition Scanner | Type any food/meal → full nutritional breakdown |
| 📸 Nutrition Label Scanner | Photo of nutrition label → AI reads it + chat Q&A about the data |

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/IbrahimFahad/RAG-MCP-Health-Assistant.git
cd RAG-MCP-Health-Assistant
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

Required keys:
- `ANTHROPIC_API_KEY` — [Get from Anthropic Console](https://console.anthropic.com)
- `SUPABASE_URL` + `SUPABASE_KEY` — [Get from Supabase](https://supabase.com)
- `TAVILY_API_KEY` — [Get from Tavily](https://tavily.com) (for web search fallback)

Optional:
- `FIRECRAWL_API_KEY` — web scraping fallback
- `AZURE_DOC_INTEL_ENDPOINT` + `AZURE_DOC_INTEL_KEY` — Arabic PDF OCR

### 5. Set up Supabase tables

**For RAG (Health Q&A)** — run in your Supabase SQL Editor:
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

**For Nutrition Label Scanner** — run `scripts/nutrition_table.sql`

### 6. Seed the knowledge base (optional)
```bash
python scripts/seed_database.py
```

### 7. Run the app
```bash
streamlit run frontend/app.py
```

Open **http://localhost:8501**

---

## 📁 Project Structure

```
RAG-MCP-Health-Assistant/
├── app/
│   ├── config.py                    # API keys and settings
│   ├── services/                    # Business logic (one folder/file per service)
│   │   ├── food_nutrition_scanner/
│   │   ├── nutrition_scanner/
│   │   ├── lab_reader.py
│   │   ├── medicine_info.py
│   │   └── triage.py
│   ├── mcp_tools/                   # Shared AI utilities
│   └── agent/                       # RAG pipeline and agent loop
├── frontend/
│   ├── app.py                       # Dashboard home page
│   ├── utils.py                     # Sidebar, styles, dark/light mode, t() helper
│   └── pages/                       # One .py file per page/service
├── scripts/                         # SQL and setup scripts
├── .env.example                     # Template for environment variables
└── requirements.txt
```

---

## ➕ How to Add a New Service (for collaborators)

1. **Fork** this repo on GitHub
2. **Create a branch**: `git checkout -b feature/my-service-name`
3. **Create the service logic**:
   ```
   app/services/my_service/__init__.py   (empty)
   app/services/my_service/service.py    (your logic)
   ```
4. **Create the page** `frontend/pages/my_service.py` — always start with:
   ```python
   import sys, os
   sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
   from dotenv import load_dotenv
   load_dotenv(override=True)
   import streamlit as st
   from frontend.utils import apply_global_styles, render_sidebar, t
   st.set_page_config(page_title="My Service | MediAssist", page_icon="🔧", layout="wide", initial_sidebar_state="expanded")
   apply_global_styles()
   lang = render_sidebar(active="my_service")
   ```
5. **Add to sidebar** in `frontend/utils.py` — add a tuple to the `pages` list
6. **Add a dashboard card** in `frontend/app.py`
7. **Push and open a Pull Request** on GitHub

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| LLM + Vision | Claude Sonnet 4.6 (Anthropic) |
| Frontend | Streamlit — bilingual, dark/light mode |
| Database | Supabase (pgvector for RAG + regular tables) |
| Embeddings | `intfloat/multilingual-e5-large` |
| Web Search | Tavily API |
| Web Scraping | BeautifulSoup / Firecrawl |
| Medical Literature | PubMed NIH API |

---

## 🤝 Contributing

Pull requests are welcome! Fork → branch → commit → PR.

---

## ⚠️ Disclaimer

MediAssist is a college project for **educational purposes only**. It does not replace professional medical advice. Always consult a qualified healthcare provider.