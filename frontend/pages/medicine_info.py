import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from frontend.utils import apply_global_styles, render_sidebar, t
from app.services.medicine_info import answer_medicine_question

st.set_page_config(
    page_title="Medicine Info | MediAssist",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_global_styles()
lang = render_sidebar(active="medicine_info")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="page-title">💊 {t("Medicine Information", "معلومات الأدوية", lang)}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="page-subtitle">'
    f'{t("Type a medicine name or ask a question about dosage, side effects, or interactions.", "اكتب اسم دواء أو اسأل عن الجرعة أو الآثار الجانبية أو التفاعلات.", lang)}'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Session state ─────────────────────────────────────────────────────────────
if "med_chat_history" not in st.session_state:
    st.session_state.med_chat_history = []
if "med_followups" not in st.session_state:
    st.session_state.med_followups = []
if "med_sources" not in st.session_state:
    st.session_state.med_sources = []

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.med_chat_history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("lang") == "ar":
            st.markdown(f'<div class="rtl">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# Sources from last answer
if st.session_state.med_sources:
    with st.expander(t("📚 Sources", "📚 المصادر", lang), expanded=False):
        for src in st.session_state.med_sources:
            st.markdown(f"- {src}")

# Follow-up buttons
if st.session_state.med_followups:
    st.markdown(
        f'<p style="font-size:13px;font-weight:600;color:var(--text);margin-top:8px;">💡 {t("You might also ask:", "قد تسأل أيضاً:", lang)}</p>',
        unsafe_allow_html=True,
    )
    for fq in st.session_state.med_followups:
        if st.button(fq, key=f"fq_{hash(fq)}"):
            st.session_state.med_pending = fq
            st.rerun()

# ── Input ─────────────────────────────────────────────────────────────────────
if "med_pending" in st.session_state:
    question = st.session_state.pop("med_pending")
else:
    question = st.chat_input(
        t("e.g. What are the side effects of ibuprofen?", "مثال: ما هي الآثار الجانبية للإيبوبروفين؟", lang)
    )

if question:
    # Show user message
    st.session_state.med_chat_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        if lang == "ar":
            st.markdown(f'<div class="rtl">{question}</div>', unsafe_allow_html=True)
        else:
            st.markdown(question)

    # Build API history (exclude last user msg we just appended)
    api_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.med_chat_history[:-1]
    ]

    with st.chat_message("assistant"):
        with st.spinner(t("Searching medicine database...", "جاري البحث في قاعدة بيانات الأدوية...", lang)):
            try:
                result = answer_medicine_question(question, history=api_history)
                answer = result["answer"]
                answer_lang = result["language"]
                src_type = result.get("source_type", "none")
                st.session_state.med_followups = result["followups"]
                st.session_state.med_sources = result["sources"]

                # Source badge
                if src_type == "database":
                    st.markdown('<span style="background:#e8f5f0;color:#2a9e78;padding:3px 10px;border-radius:12px;font-size:12px;">📦 DB</span>', unsafe_allow_html=True)
                elif src_type == "fda_api":
                    st.markdown('<span style="background:#ddeef8;color:#185fa5;padding:3px 10px;border-radius:12px;font-size:12px;">🌐 FDA API</span>', unsafe_allow_html=True)
                elif src_type == "web_search":
                    st.markdown('<span style="background:#fef6e0;color:#854f0b;padding:3px 10px;border-radius:12px;font-size:12px;">🔍 Web</span>', unsafe_allow_html=True)

                if answer_lang == "ar":
                    st.markdown(f'<div class="rtl">{answer}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(answer)

            except Exception as exc:
                answer = t(f"An error occurred: {exc}", f"حدث خطأ: {exc}", lang)
                answer_lang = lang
                src_type = "none"
                st.error(answer)

    st.session_state.med_chat_history.append({"role": "assistant", "content": answer, "lang": answer_lang})
    st.rerun()

# ── Clear button ──────────────────────────────────────────────────────────────
if st.session_state.med_chat_history:
    if st.button(t("🗑️ Clear conversation", "🗑️ مسح المحادثة", lang)):
        st.session_state.med_chat_history = []
        st.session_state.med_followups = []
        st.session_state.med_sources = []
        st.rerun()

# ── Empty state ───────────────────────────────────────────────────────────────
if not st.session_state.med_chat_history:
    st.markdown(
        f"""<div style="background:var(--card);border:2px dashed rgba(61,191,148,0.3);border-radius:14px;
                     padding:48px;text-align:center;color:#94a3b8;margin-top:24px;">
            <div style="font-size:3rem;">💊</div>
            <div style="font-size:1.1rem;font-weight:600;color:var(--text-mid);margin-top:12px;">
                {t("Ask about any medicine", "اسأل عن أي دواء", lang)}
            </div>
            <div style="font-size:0.88rem;margin-top:8px;">
                {t("Examples: side effects of paracetamol · ibuprofen dosage · can I take X with Y",
                   "أمثلة: آثار جانبية للباراسيتامول · جرعة الإيبوبروفين · هل يمكن تناول X مع Y", lang)}
            </div>
        </div>""",
        unsafe_allow_html=True,
    )