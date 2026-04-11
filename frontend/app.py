import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from app.agent.rag_pipeline import process_query

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Health Assistant | المساعد الصحي",
    page_icon="🩺",
    layout="centered",
)

# ── RTL + styling ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* RTL support for Arabic */
    .rtl { direction: rtl; text-align: right; font-family: 'Arial', sans-serif; }
    .ltr { direction: ltr; text-align: left; }

    /* Source badge */
    .badge-db  { background:#1a7f37; color:white; padding:2px 10px; border-radius:12px; font-size:13px; }
    .badge-web { background:#0969da; color:white; padding:2px 10px; border-radius:12px; font-size:13px; }

    /* Score bar */
    .score-bar { font-size:13px; color:#666; margin-bottom:8px; }

    /* Follow-up buttons */
    .followup-title { font-size:14px; font-weight:600; color:#444; margin-top:12px; }

    /* Chat message spacing */
    .stChatMessage { margin-bottom: 8px; }

    /* Disclaimer styling */
    blockquote { border-left: 4px solid #e36209; padding-left:12px; color:#666; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []       # chat history for display
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []  # Claude message history for multi-turn
if "language" not in st.session_state:
    st.session_state.language = "en"

# ── Header ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🩺 Health Assistant | المساعد الصحي")
with col2:
    # Step 39: Language toggle
    lang = st.selectbox(
        "Language",
        options=["English", "العربية"],
        index=0 if st.session_state.language == "en" else 1,
        label_visibility="collapsed"
    )
    st.session_state.language = "en" if lang == "English" else "ar"

# Subtitle changes based on language
if st.session_state.language == "ar":
    st.markdown('<p class="rtl" style="color:#666">اسألني أي سؤال صحي — سأجيبك بمعلومات موثوقة من مصادر طبية معتمدة.</p>', unsafe_allow_html=True)
else:
    st.caption("Ask me any health question — I'll answer using trusted medical sources.")

st.divider()

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            # Step 42: Source badge (DB vs web)
            source = msg.get("source", "")
            score  = msg.get("best_score", 0)
            tools  = msg.get("tools_used", [])

            meta_col1, meta_col2 = st.columns([1, 3])
            with meta_col1:
                if source == "database":
                    st.markdown('<span class="badge-db">📦 From DB</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="badge-web">🌐 Web Search</span>', unsafe_allow_html=True)

            # Step 41: Confidence score
            with meta_col2:
                if score > 0:
                    st.markdown(f'<span class="score-bar">Confidence: {score:.0%}</span>', unsafe_allow_html=True)
                if tools:
                    st.markdown(f'<span class="score-bar">Tools: {", ".join(tools)}</span>', unsafe_allow_html=True)

            # Step 43: RTL for Arabic answers
            if msg.get("language") == "ar":
                st.markdown(f'<div class="rtl">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])

            # Step 40: Source citations
            sources = msg.get("sources", [])
            if sources:
                with st.expander("📚 Sources"):
                    for s in sources:
                        if s:
                            st.markdown(f"- {s}")

            # Follow-up questions
            followups = msg.get("followups", [])
            if followups:
                st.markdown('<p class="followup-title">💡 You might also ask:</p>', unsafe_allow_html=True)
                for fq in followups:
                    if st.button(fq, key=f"fq_{hash(fq)}"):
                        st.session_state.pending_query = fq
                        st.rerun()
        else:
            # Step 43: RTL for Arabic user messages
            if st.session_state.language == "ar":
                st.markdown(f'<div class="rtl">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
placeholder = "اكتب سؤالك الصحي هنا..." if st.session_state.language == "ar" else "Ask a health question..."

# Handle follow-up button clicks
if "pending_query" in st.session_state:
    user_input = st.session_state.pop("pending_query")
else:
    user_input = st.chat_input(placeholder)

if user_input:
    # Add user message to display
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        if st.session_state.language == "ar":
            st.markdown(f'<div class="rtl">{user_input}</div>', unsafe_allow_html=True)
        else:
            st.markdown(user_input)

    # Run the pipeline
    with st.chat_message("assistant"):
        with st.spinner("Thinking..." if st.session_state.language == "en" else "جاري البحث..."):
            result = process_query(
                query=user_input,
                chat_history=st.session_state.agent_history,
            )

        source = result["source"]
        score  = result["best_score"]
        tools  = result["tools_used"]
        lang   = result["language"]

        # Step 42: Source badge
        meta_col1, meta_col2 = st.columns([1, 3])
        with meta_col1:
            if source == "database":
                st.markdown('<span class="badge-db">📦 From DB</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge-web">🌐 Web Search</span>', unsafe_allow_html=True)
        with meta_col2:
            if score > 0:
                st.markdown(f'<span class="score-bar">Confidence: {score:.0%}</span>', unsafe_allow_html=True)
            if tools:
                st.markdown(f'<span class="score-bar">Tools: {", ".join(tools)}</span>', unsafe_allow_html=True)

        # Step 43: RTL Arabic
        if lang == "ar":
            st.markdown(f'<div class="rtl">{result["answer"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(result["answer"])

        # Step 40: Sources
        if result["sources"]:
            with st.expander("📚 Sources"):
                for s in result["sources"]:
                    if s:
                        st.markdown(f"- {s}")

        # Follow-ups
        if result["followups"]:
            st.markdown('<p class="followup-title">💡 You might also ask:</p>', unsafe_allow_html=True)
            for fq in result["followups"]:
                if st.button(fq, key=f"fq_new_{hash(fq)}"):
                    st.session_state.pending_query = fq
                    st.rerun()

    # Save to history
    st.session_state.messages.append({
        "role":       "assistant",
        "content":    result["answer"],
        "source":     source,
        "best_score": score,
        "tools_used": tools,
        "language":   lang,
        "sources":    result["sources"],
        "followups":  result["followups"],
    })

    # Update Claude's conversation history for multi-turn
    st.session_state.agent_history.append({"role": "user", "content": user_input})
    st.session_state.agent_history.append({"role": "assistant", "content": result["answer"][:500]})

# ── Clear chat button ─────────────────────────────────────────────────────────
if st.session_state.messages:
    if st.button("🗑️ Clear chat" if st.session_state.language == "en" else "🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.session_state.agent_history = []
        st.rerun()