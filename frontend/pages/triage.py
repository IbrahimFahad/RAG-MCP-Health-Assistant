import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from frontend.utils import apply_global_styles, render_sidebar, t
from app.services.triage import (
    SEVERITY_META,
    get_node,
    get_question,
    get_next,
    get_result,
    is_terminal,
)

st.set_page_config(
    page_title="Emergency Triage | MediAssist",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_global_styles()
lang = render_sidebar(active="triage")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="page-title">🚑 {t("Emergency Triage", "الفرز الطارئ", lang)}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="page-subtitle">'
    f'{t("Answer a few yes/no questions to find out how urgently you need medical care.", "أجب على بعض الأسئلة بنعم/لا لمعرفة مدى إلحاح حاجتك للرعاية الطبية.", lang)}'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Session state init ────────────────────────────────────────────────────────
if "triage_node" not in st.session_state:
    st.session_state.triage_node = "start"
if "triage_history" not in st.session_state:
    st.session_state.triage_history = []   # list of (question, answer)
if "triage_done" not in st.session_state:
    st.session_state.triage_done = False

# ── Helper: restart ───────────────────────────────────────────────────────────
def restart():
    st.session_state.triage_node    = "start"
    st.session_state.triage_history = []
    st.session_state.triage_done    = False

# ── DONE state: show result ───────────────────────────────────────────────────
if st.session_state.triage_done:
    result = get_result(st.session_state.triage_node, lang)
    meta   = SEVERITY_META[result["level"]]

    # Big severity banner
    st.markdown(
        f"""<div style="background:{meta['bg']};border:2px solid {meta['border']};
                     border-radius:14px;padding:24px 28px;margin-bottom:20px;">
            <div style="font-size:2rem;margin-bottom:4px;">{meta['icon']}</div>
            <div style="font-size:1.4rem;font-weight:700;color:{meta['color']};">
                {result['label']}
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Advice box
    advice_html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', result["advice"])
    advice_html = advice_html.replace("\n", "<br>")

    st.markdown(
        f"""<div style="background:var(--card);border:1px solid var(--border);border-radius:10px;
                     padding:20px 24px;margin-bottom:20px;font-size:0.95rem;
                     color:var(--text);line-height:1.7;">
            {advice_html}
        </div>""",
        unsafe_allow_html=True,
    )

    # Questions summary
    if st.session_state.triage_history:
        with st.expander(t("📋 Your Answers", "📋 إجاباتك", lang)):
            for i, (q, ans) in enumerate(st.session_state.triage_history, 1):
                ans_label = (
                    (t("Yes", "نعم", lang) if ans else t("No", "لا", lang))
                )
                ans_color = "#22c55e" if ans else "var(--text-muted)"
                st.markdown(
                    f'<div style="padding:6px 0;border-bottom:1px solid #f1f5f9;">'
                    f'<span style="color:var(--text-muted);font-size:0.85rem;">{i}.</span> '
                    f'{q} '
                    f'<span style="color:{ans_color};font-weight:600;">{ans_label}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # Disclaimer
    st.markdown(
        f"""<div style="background:#fef9ec;border-left:3px solid #f0b429;border:none;border-left:3px solid #f0b429;border-radius:8px;
                     padding:12px 16px;font-size:0.82rem;color:#7a6030;margin-top:8px;">
            ⚠️ <b>{t("Disclaimer:", "إخلاء المسؤولية:", lang)}</b>
            {t(
                "This triage tool provides general guidance only and does not replace professional "
                "medical diagnosis. In any life-threatening situation, always call emergency services immediately.",
                "هذه الأداة تقدم إرشادات عامة فقط ولا تحل محل التشخيص الطبي المتخصص. "
                "في أي حالة تهدد الحياة، اتصل دائماً بخدمات الطوارئ فوراً.",
                lang,
            )}
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(
        "🔄 " + t("Start Again", "ابدأ من جديد", lang),
        type="secondary",
        use_container_width=False,
    ):
        restart()
        st.rerun()

# ── Active question state ─────────────────────────────────────────────────────
else:
    current_node = st.session_state.triage_node

    # Progress indicator (max ~6 questions deep)
    step = len(st.session_state.triage_history) + 1
    progress_pct = min(100, (step / 6) * 100)
    st.markdown(
        f"""<div style="margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span style="font-size:0.8rem;color:var(--text-muted);">{t("Question","السؤال",lang)} {step}</span>
                <span style="font-size:0.75rem;color:var(--text-muted);">{step}/6</span>
            </div>
            <div style="height:4px;background:#e8f5f0;border-radius:2px;">
                <div style="height:4px;background:#3dbf94;border-radius:2px;width:{progress_pct:.0f}%;transition:width 0.3s;"></div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("""
<style>
div[data-testid="column"]:nth-child(1) .stButton > button:hover {
    background: #fdeaea !important;
    border-color: #e24b4a !important;
    color: #e24b4a !important;
}
div[data-testid="column"]:nth-child(2) .stButton > button:hover {
    background: #e8f5f0 !important;
    border-color: #3dbf94 !important;
    color: #2a9e78 !important;
}
</style>
""", unsafe_allow_html=True)

    # Question card
    question_text = get_question(current_node, lang)
    st.markdown(
        f"""<div style="background:var(--card);border:1px solid var(--border);border-radius:14px;
                     padding:28px 28px 24px;margin-bottom:20px;
                     box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="font-size:1.15rem;font-weight:600;color:var(--text);line-height:1.5;">
                {"<div class='rtl'>" if lang == "ar" else ""}{question_text}{"</div>" if lang == "ar" else ""}
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Yes / No buttons
    btn_col1, btn_col2, _ = st.columns([1, 1, 3])
    yes_clicked = btn_col1.button(
        "✅ " + t("Yes", "نعم", lang),
        type="primary",
        use_container_width=True,
        key="yes_btn",
    )
    no_clicked = btn_col2.button(
        "❌ " + t("No", "لا", lang),
        type="secondary",
        use_container_width=True,
        key="no_btn",
    )

    if yes_clicked or no_clicked:
        answer = yes_clicked  # True = yes, False = no
        # Save to history
        st.session_state.triage_history.append((question_text, answer))
        # Advance tree
        next_node = get_next(current_node, answer)
        st.session_state.triage_node = next_node

        if is_terminal(next_node):
            st.session_state.triage_done = True

        st.rerun()

    # Previous answers breadcrumb
    if st.session_state.triage_history:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.8rem;color:#94a3b8;">'
            f'{t("Previous answers:", "الإجابات السابقة:", lang)}</div>',
            unsafe_allow_html=True,
        )
        for q, ans in st.session_state.triage_history:
            ans_label = t("Yes", "نعم", lang) if ans else t("No", "لا", lang)
            ans_color = "#22c55e" if ans else "var(--text-muted)"
            short_q = q[:60] + "..." if len(q) > 60 else q
            st.markdown(
                f'<div style="font-size:0.82rem;color:var(--text-muted);padding:3px 0;">'
                f'{short_q} → <span style="color:{ans_color};font-weight:600;">{ans_label}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Restart link
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(
        "↩ " + t("Start Over", "ابدأ من البداية", lang),
        type="secondary",
        key="restart_mid",
    ):
        restart()
        st.rerun()

    # ── Always-visible emergency reminder ─────────────────────────────────────
    st.markdown(
        f"""<div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;
                     padding:10px 14px;font-size:0.82rem;color:#991b1b;margin-top:24px;">
            🚨 <b>{t("In an obvious emergency, don't wait — call 911/999 immediately.",
                       "في حالة طوارئ واضحة، لا تنتظر — اتصل بالطوارئ 911/999 فوراً.", lang)}</b>
        </div>""",
        unsafe_allow_html=True,
    )