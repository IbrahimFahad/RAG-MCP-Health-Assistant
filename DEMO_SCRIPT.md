# Demo Script — Agentic RAG Health Assistant

## Setup (before presentation)

1. Run: `python scripts/seed_database.py` (only needed once)
2. Run: `python -m streamlit run frontend/app.py`
3. Open: http://localhost:8501

---

## Demo Flow

### Scene 1: DB Hit (Fast Answer)
**Say:** "The system has a pre-populated health knowledge base. Watch how fast it answers known topics."

**Type:** `What are the symptoms of diabetes?`

**Point out:**
- Badge shows **📦 From DB**
- Confidence score (should be ~90%)
- No tools called — instant answer
- Follow-up questions at the bottom

---

### Scene 2: Web Search Fallback
**Say:** "Now I'll ask something not in the database. Watch the agent kick in."

**Type:** `What are the side effects of ibuprofen?`

**Point out:**
- Badge shows **🌐 Web Search**
- Tools used: pubmed_search, web_search, store_to_db
- Sources panel shows real medical URLs
- Medical disclaimer appended automatically

---

### Scene 3: Arabic Query
**Say:** "The system is fully bilingual — Arabic and English in the same vector space."

**Switch language toggle to العربية**

**Type:** `ما هي أعراض ارتفاع ضغط الدم؟`

**Point out:**
- Language detected as Arabic automatically
- Answer comes in Arabic
- RTL text layout
- Arabic disclaimer appended

---

### Scene 4: Cross-lingual Retrieval
**Say:** "Now the impressive part — Arabic question answered from English documents."

**Switch back to English toggle but type Arabic:**

**Type:** `ما هي أسباب أمراض القلب؟`

**Point out:**
- Arabic query matched English cardiovascular document
- Shows the multilingual-e5-large embedding power
- Same vector space for both languages

---

### Scene 5: Health Calculator
**Say:** "The system also has built-in health calculators."

**Type:** `Calculate my BMI, I weigh 80kg and I am 175cm tall`

**Point out:**
- Agent calls calculate_bmi tool directly
- Returns BMI value, WHO category, and advice
- No web search needed

---

### Scene 6: DB Caching (Ask Again)
**Say:** "Remember the ibuprofen question from Scene 2? Let's ask it again."

**Type:** `What are the side effects of ibuprofen?`

**Point out:**
- Now shows **📦 From DB** — cached from the first search
- No tools called this time
- This is the self-learning behavior of the system

---

## Key Technical Points to Mention

1. **Vector similarity search** — not keyword matching, understands meaning
2. **multilingual-e5-large** — 1024-dim embeddings, Arabic + English same space
3. **Self-learning** — stores web results back to DB automatically
4. **Trusted sources only** — WHO, NHS, Mayo Clinic, NIH whitelisted
5. **Medical disclaimers** — auto-injected, type-aware (general/medication/emergency)
6. **MCP architecture** — tools are modular, can add new ones easily
