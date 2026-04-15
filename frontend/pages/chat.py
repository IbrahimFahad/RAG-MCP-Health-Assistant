import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from frontend.utils import apply_global_styles, render_sidebar, t
from app.agent.rag_pipeline import process_query

st.set_page_config(page_title="Health Q&A | MediAssist", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")
apply_global_styles()
lang = render_sidebar(active="chat")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(f'<div class="page-title">🩺 {t("Health Q&A", "الأسئلة الصحية", lang)}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-subtitle">{t("Ask any health question — answered from trusted medical sources.", "اسأل أي سؤال صحي — مجاب من مصادر طبية موثوقة.", lang)}</div>', unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            m1, m2 = st.columns([1, 3])
            with m1:
                if msg.get("source") == "database":
                    st.markdown('<span style="background:#dcfce7;color:#166534;padding:3px 10px;border-radius:12px;font-size:12px;">📦 DB</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="background:#dbeafe;color:#1e40af;padding:3px 10px;border-radius:12px;font-size:12px;">🌐 Web</span>', unsafe_allow_html=True)
            with m2:
                if msg.get("best_score", 0) > 0:
                    st.markdown(f'<span style="font-size:12px;color:#64748b;">Confidence: {msg["best_score"]:.0%}</span>', unsafe_allow_html=True)
                if msg.get("tools_used"):
                    st.markdown(f'<span style="font-size:12px;color:#64748b;">Tools: {", ".join(msg["tools_used"])}</span>', unsafe_allow_html=True)

            if msg.get("language") == "ar":
                st.markdown(f'<div class="rtl">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])

            if msg.get("sources"):
                with st.expander(t("📚 Sources", "📚 المصادر", lang)):
                    for s in msg["sources"]:
                        if s:
                            st.markdown(f"- {s}")

            if msg.get("followups"):
                st.markdown(f'<p style="font-size:13px;font-weight:600;color:#0a2540;margin-top:8px;">💡 {t("You might also ask:", "قد تسأل أيضاً:", lang)}</p>', unsafe_allow_html=True)
                for fq in msg["followups"]:
                    if st.button(fq, key=f"fq_{hash(fq)}"):
                        st.session_state.pending_query = fq
                        st.rerun()
        else:
            if msg.get("lang") == "ar":
                st.markdown(f'<div class="rtl">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
if "pending_query" in st.session_state:
    user_input = st.session_state.pop("pending_query")
else:
    user_input = st.chat_input(t("Ask a health question...", "اكتب سؤالك الصحي هنا...", lang))

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input, "lang": lang})
    with st.chat_message("user"):
        if lang == "ar":
            st.markdown(f'<div class="rtl">{user_input}</div>', unsafe_allow_html=True)
        else:
            st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner(t("Searching...", "جاري البحث...", lang)):
            result = process_query(user_input, chat_history=st.session_state.agent_history)

        m1, m2 = st.columns([1, 3])
        with m1:
            if result["source"] == "database":
                st.markdown('<span style="background:#dcfce7;color:#166534;padding:3px 10px;border-radius:12px;font-size:12px;">📦 DB</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span style="background:#dbeafe;color:#1e40af;padding:3px 10px;border-radius:12px;font-size:12px;">🌐 Web</span>', unsafe_allow_html=True)
        with m2:
            if result["best_score"] > 0:
                st.markdown(f'<span style="font-size:12px;color:#64748b;">Confidence: {result["best_score"]:.0%}</span>', unsafe_allow_html=True)
            if result["tools_used"]:
                st.markdown(f'<span style="font-size:12px;color:#64748b;">Tools: {", ".join(result["tools_used"])}</span>', unsafe_allow_html=True)

        if result["language"] == "ar":
            st.markdown(f'<div class="rtl">{result["answer"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(result["answer"])

        if result["sources"]:
            with st.expander(t("📚 Sources", "📚 المصادر", lang)):
                for s in result["sources"]:
                    if s:
                        st.markdown(f"- {s}")

        if result["followups"]:
            st.markdown(f'<p style="font-size:13px;font-weight:600;color:#0a2540;margin-top:8px;">💡 {t("You might also ask:", "قد تسأل أيضاً:", lang)}</p>', unsafe_allow_html=True)
            for fq in result["followups"]:
                if st.button(fq, key=f"fq_new_{hash(fq)}"):
                    st.session_state.pending_query = fq
                    st.rerun()

    st.session_state.messages.append({
        "role": "assistant", "content": result["answer"],
        "source": result["source"], "best_score": result["best_score"],
        "tools_used": result["tools_used"], "language": result["language"],
        "sources": result["sources"], "followups": result["followups"],
    })
    st.session_state.agent_history.append({"role": "user", "content": user_input})
    st.session_state.agent_history.append({"role": "assistant", "content": result["answer"][:500]})

if st.session_state.messages:
    if st.button(t("🗑️ Clear chat", "🗑️ مسح المحادثة", lang)):
        st.session_state.messages = []
        st.session_state.agent_history = []
        st.rerun()