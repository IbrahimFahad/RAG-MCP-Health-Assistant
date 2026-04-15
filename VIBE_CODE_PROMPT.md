# Vibe Code Context Prompt
# Copy this entire prompt into your Vibe Code session at the start.

---

You are helping build a new health service module that will be integrated into an existing AI health platform called **MediAssist**. Read all the context below carefully before doing anything. After reading, ask me: **"What service are we building?"** — then proceed only after I answer.

---

## The Existing Platform (DO NOT REBUILD ANY OF THIS)

### What MediAssist already has:
The main platform is a bilingual (Arabic + English) Agentic RAG health assistant. It is fully built. Your job is to build ONE new service module that plugs into it — not rebuild the platform.

### Tech stack already in place:
- **Python 3.10**
- **Streamlit** — frontend UI framework
- **Claude API** (`claude-sonnet-4-6`) via `anthropic` Python package — already configured
- **Supabase** — PostgreSQL + pgvector for vector similarity search
- **multilingual-e5-large** — HuggingFace embedding model, 1024-dim, handles Arabic + English in same vector space — already loaded and running
- **Tavily** — web search API — already integrated
- **BeautifulSoup** — web scraping — already integrated
- **PubMed NIH API** — medical literature search — already integrated
- **langdetect** — Arabic/English language detection — already integrated
- **PyMuPDF (fitz)** — PDF loading — already integrated

### Folder structure of the main project:
```
RAG-MCP/
├── app/
│   ├── agent/
│   │   ├── agent_loop.py          # Claude API loop with tool calling
│   │   ├── rag_pipeline.py        # Main pipeline: detect language → retrieve → agent → answer
│   │   ├── tool_definitions.py    # MCP tool schemas for Claude
│   │   └── tool_executor.py       # Runs tools when Claude calls them
│   ├── embeddings/
│   │   ├── embedder.py            # embed_query(text) and embed_passage(text) → list[float] 1024-dim
│   │   ├── chunker.py             # chunk_text(text) → list[str], sentence-aware, 400 token max
│   │   ├── loader.py              # load_pdf(path), load_text(path) → Document
│   │   └── pipeline.py            # load_and_chunk(file), load_and_chunk_string(text) → list[dict with embeddings]
│   ├── mcp_tools/
│   │   ├── web_search.py          # web_search(query) → list[dict]
│   │   ├── web_scraper.py         # scrape(url) → dict with text
│   │   ├── pubmed_search.py       # search_pubmed(query) → list[dict with abstracts]
│   │   ├── store_to_db.py         # store_to_db(text, title, source_url, source_type) → dict
│   │   ├── source_validator.py    # validate_source(url) → dict, filter_trusted_results(list)
│   │   ├── health_calculators.py  # calculate_bmi, calculate_bmr, calculate_ideal_weight
│   │   ├── disclaimer_injector.py # inject_disclaimer(answer, language) → str
│   │   ├── followup_generator.py  # generate_followups(question, answer, language) → list[str]
│   │   └── language_detector.py   # detect_language(text) → 'ar' or 'en'
│   ├── retrieval/
│   │   ├── search.py              # retrieve(query) → dict, should_use_web(result) → bool
│   │   └── store.py               # ingest_text(text, title, source), ingest_file(path)
│   └── config.py                  # All API keys loaded from .env via load_dotenv(override=True)
├── frontend/
│   ├── app.py                     # Dashboard home page with service cards
│   ├── utils.py                   # apply_global_styles(), render_sidebar(active), t(en, ar, lang)
│   └── pages/
│       ├── chat.py                # Health Q&A chat page
│       └── calculators.py         # BMI / Calories / Ideal Weight calculators
├── .env                           # API keys (not committed to git)
└── requirements.txt
```

### Available imports you CAN and SHOULD use (don't rewrite):
```python
# Embed text into 1024-dim vector
from app.embeddings.embedder import embed_query, embed_passage

# Chunk a long document into smaller pieces
from app.embeddings.chunker import chunk_text

# Load PDF or text file
from app.embeddings.loader import load_pdf, load_text, load_from_string

# Store content to vector DB (full pipeline: chunk → embed → store)
from app.retrieval.store import ingest_text, ingest_file

# Search vector DB for similar content
from app.retrieval.search import retrieve, should_use_web

# Call Claude API
import anthropic
from app.config import ANTHROPIC_API_KEY
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Detect language
from app.mcp_tools.language_detector import detect_language

# Inject medical disclaimer
from app.mcp_tools.disclaimer_injector import inject_disclaimer

# Generate follow-up questions
from app.mcp_tools.followup_generator import generate_followups

# Load env vars
from app.config import ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_KEY

# UI helpers (same look as the rest of the platform)
from frontend.utils import apply_global_styles, render_sidebar, t
```

### Supabase vector DB schema:
```sql
health_knowledge (
    id          BIGSERIAL PRIMARY KEY,
    content     TEXT,
    embedding   VECTOR(1024),
    language    VARCHAR(10),     -- 'ar' or 'en'
    source_url  TEXT,
    source_type VARCHAR(50),     -- 'web', 'pubmed', 'pdf', 'manual'
    title       TEXT,
    metadata    JSONB,
    created_at  TIMESTAMPTZ
)
```

### Dashboard design system:
The platform uses a dark blue sidebar (`#0a2540`) with white cards. The UI helper functions handle all styling. Your page MUST use these:
```python
st.set_page_config(page_title="Your Service | MediAssist", page_icon="🔧", layout="wide", initial_sidebar_state="expanded")
apply_global_styles()   # applies platform CSS
lang = render_sidebar(active="your_service_key")  # renders sidebar, returns 'en' or 'ar'
```
For Arabic RTL text: `st.markdown('<div class="rtl">النص العربي</div>', unsafe_allow_html=True)`
For translations: `t("English text", "النص العربي", lang)`

---

## What you need to build

After I tell you the service name, build ONLY:

```
your_service_name/              ← one folder, this is what you send back
├── page.py                     ← the Streamlit page (goes into frontend/pages/)
├── service.py                  ← the core logic (goes into app/services/)
├── requirements_extra.txt      ← any NEW packages needed (not already in requirements.txt)
│                                  Leave empty if no new packages needed
└── README_integration.md       ← 3-5 line note: what the service does + any setup steps
```

### Rules for the output folder:
1. **DO NOT** include: `app/`, `frontend/utils.py`, `.env`, `requirements.txt`, or any file that already exists in the main project
2. **DO NOT** rewrite embedding, retrieval, or Claude API logic — import from existing modules
3. `page.py` must use `apply_global_styles()` and `render_sidebar()` from `frontend.utils`
4. `service.py` must be importable standalone — no Streamlit calls inside it, only logic
5. All API keys must be loaded from `app.config` — do not hardcode keys or create new .env entries unless the service needs a completely new API key
6. If a new API key is needed, add it to `requirements_extra.txt` with a comment explaining what it's for
7. Arabic/English support is required — use `detect_language()` and respond in the user's language
8. Append medical disclaimers using `inject_disclaimer()` — do not write custom disclaimers

---

## Now ask me: "What service are we building?"