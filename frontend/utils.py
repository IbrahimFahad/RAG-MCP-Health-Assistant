import streamlit as st

# ── Translation helper ────────────────────────────────────────────────────────
def t(en: str, ar: str, lang: str) -> str:
    return ar if lang == "ar" else en


# ── Design tokens ─────────────────────────────────────────────────────────────
def _tokens(dark: bool) -> dict:
    if dark:
        return {
            "bg": "#111d18", "card": "#1a2a24", "text": "#e2f0eb",
            "text_mid": "#a8cbbf", "text_muted": "#6a9b8a",
            "sidebar": "#131f1a", "mint": "#1a2e26", "mint2": "#1f3a2e",
            "border": "rgba(61,191,148,0.12)", "input_bg": "#1e2e28",
        }
    return {
        "bg": "#f0f8f4", "card": "#ffffff", "text": "#1a2e2a",
        "text_mid": "#4a6b62", "text_muted": "#8aab9f",
        "sidebar": "#ffffff", "mint": "#e8f5f0", "mint2": "#d0ede3",
        "border": "rgba(60,150,110,0.12)", "input_bg": "#ffffff",
    }


# ── Global CSS + JS ───────────────────────────────────────────────────────────
def apply_global_styles():
    theme = st.session_state.get("theme", "light")
    dark = theme == "dark"
    T = _tokens(dark)

    disc_bg   = "#1f1a0e" if dark else "#fef9ec"
    disc_text = "#c4a04a" if dark else "#7a6030"
    disc_border = "#b08020" if dark else "#f0b429"

    st.markdown(f"""
<style>
/* ── CSS tokens ── */
:root {{
    --teal: #3dbf94;
    --teal-dark: #2a9e78;
    --bg: {T['bg']};
    --card: {T['card']};
    --text: {T['text']};
    --text-mid: {T['text_mid']};
    --text-muted: {T['text_muted']};
    --sidebar: {T['sidebar']};
    --mint: {T['mint']};
    --mint2: {T['mint2']};
    --border: {T['border']};
    --input-bg: {T['input_bg']};
}}

/* ── Page background ── */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > div,
.block-container {{
    background: var(--bg) !important;
}}

/* ── Hide Streamlit auto-generated page nav ── */
[data-testid="stSidebarNav"] {{
    display: none !important;
}}

/* ── Keep sidebar toggle always visible ── */
[data-testid="collapsedControl"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: #3dbf94 !important;
    border-radius: 0 10px 10px 0 !important;
    padding: 10px 6px !important;
    box-shadow: 2px 0 8px rgba(61,191,148,0.35) !important;
    top: 50% !important;
}}
[data-testid="collapsedControl"] svg {{
    fill: white !important;
    color: white !important;
    stroke: white !important;
}}
[data-testid="collapsedControl"] button {{
    background: transparent !important;
    border: none !important;
    color: white !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: var(--sidebar) !important;
    border-right: 1px solid var(--border) !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label {{
    color: var(--text) !important;
}}

/* ── Sidebar nav buttons — left-aligned, transparent bg ── */
[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    color: var(--text) !important;
    text-align: left !important;
    justify-content: flex-start !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 9px 16px !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    width: 100% !important;
    box-shadow: none !important;
    margin: 1px 0 !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: var(--mint) !important;
    color: var(--teal) !important;
}}

/* ── Main content buttons — teal ── */
[data-testid="stMain"] .stButton > button,
.block-container .stButton > button {{
    background: var(--teal) !important;
    color: #1a2e2a !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 11px 18px !important;
    box-shadow: none !important;
}}
[data-testid="stMain"] .stButton > button:hover,
.block-container .stButton > button:hover {{
    background: var(--teal-dark) !important;
    color: #1a2e2a !important;
}}

/* ── Text inputs ── */
.stTextInput > div > div > input {{
    background: var(--input-bg) !important;
    color: var(--text) !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 12px !important;
    font-size: 13px !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 2px rgba(61,191,148,0.15) !important;
}}
.stTextArea > div > div > textarea {{
    background: var(--input-bg) !important;
    color: var(--text) !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 12px !important;
}}

/* ── Select / Dropdowns ── */
.stSelectbox > div > div {{
    background: var(--input-bg) !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-size: 11px !important;
}}

/* ── Number inputs ── */
.stNumberInput > div > div > input {{
    background: var(--input-bg) !important;
    color: var(--text) !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 12px !important;
}}

/* ── Radio buttons ── */
.stRadio > div {{
    background: var(--mint) !important;
    border-radius: 10px !important;
    padding: 3px !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: var(--mint) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: none !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    border: none !important;
    padding: 8px 16px !important;
}}
.stTabs [aria-selected="true"] {{
    background: var(--teal) !important;
    color: #1a2e2a !important;
    font-weight: 600 !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    background: transparent !important;
    padding-top: 16px !important;
}}

/* ── Metric cards ── */
[data-testid="stMetric"] {{
    background: var(--card) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
}}
[data-testid="stMetricValue"] {{ color: var(--text) !important; }}
[data-testid="stMetricLabel"] {{ color: var(--text-muted) !important; font-size: 11px !important; }}

/* ── Expanders ── */
[data-testid="stExpander"] {{
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {{
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
    background: var(--card) !important;
    border: 2px dashed rgba(61,191,148,0.3) !important;
    border-radius: 16px !important;
}}
[data-testid="stFileUploader"]:hover {{
    background: var(--mint) !important;
    border-color: var(--teal) !important;
}}

/* ── Spinners / info boxes ── */
.stSpinner > div {{ color: var(--teal) !important; }}
.stAlert {{ border-radius: 12px !important; }}
[data-baseweb="notification"] {{ border-radius: 12px !important; }}

/* ── Divider ── */
hr {{ border-color: var(--border) !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--mint2); border-radius: 3px; }}

/* ── Shared component classes ── */
.page-title {{
    font-size: 20px; font-weight: 500; color: var(--text);
    margin-bottom: 2px; line-height: 1.3;
}}
.page-subtitle {{
    font-size: 12px; color: var(--text-muted); margin-bottom: 20px;
}}
.med-card {{
    background: var(--card);
    border-radius: 16px;
    border: 1px solid var(--border);
    padding: 20px;
}}
.chip {{
    display: inline-block;
    background: var(--mint);
    border-radius: 20px;
    padding: 6px 12px;
    font-size: 11px;
    color: #2a9e78;
    cursor: pointer;
    margin: 3px;
    transition: background 0.15s, color 0.15s;
}}
.chip:hover {{ background: var(--teal); color: #fff; }}
.disclaimer {{
    background: {disc_bg};
    border-left: 3px solid {disc_border};
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 10px;
    color: {disc_text};
    margin-top: 12px;
}}
.status-normal {{ background:#e8f5f0; color:#2a9e78; padding:3px 8px; border-radius:6px; font-size:10px; font-weight:500; }}
.status-high   {{ background:#fdeaea; color:#a32d2d; padding:3px 8px; border-radius:6px; font-size:10px; font-weight:500; }}
.status-low    {{ background:#ddeef8; color:#185fa5; padding:3px 8px; border-radius:6px; font-size:10px; font-weight:500; }}
.rtl {{ direction: rtl; text-align: right; }}

/* ── Nutrition scanner cards ── */
.nutrition-card {{
    background: var(--card) !important;
    border-radius: 16px !important;
    border: 1px solid var(--border) !important;
    padding: 20px !important;
    box-shadow: none !important;
}}
.macro-box {{
    background: var(--mint) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    padding: 14px !important;
    text-align: center !important;
}}
.macro-value {{ color: var(--text) !important; }}
.macro-label {{ color: var(--text-muted) !important; }}
.log-item {{ background: var(--card) !important; border-radius: 12px !important; }}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}
</style>

<script>
(function applyMediStyles() {{
    var dark = {'true' if dark else 'false'};
    var inputBg = dark ? '#1e2e28' : '#ffffff';
    var inputColor = dark ? '#e2f0eb' : '#1a2e2a';
    document.querySelectorAll(
        '.stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox select'
    ).forEach(function(el) {{
        el.style.background = inputBg;
        el.style.color = inputColor;
        el.style.webkitTextFillColor = inputColor;
    }});
    // Teal main buttons
    document.querySelectorAll('.block-container .stButton > button').forEach(function(btn) {{
        if (!btn.closest('[data-testid="stSidebar"]')) {{
            btn.style.background = '#3dbf94';
            btn.style.color = '#1a2e2a';
        }}
    }});
}})();
setTimeout(function() {{
    var dark = {'true' if dark else 'false'};
    var inputBg = dark ? '#1e2e28' : '#ffffff';
    var inputColor = dark ? '#e2f0eb' : '#1a2e2a';
    document.querySelectorAll('.stTextInput input, .stTextArea textarea, .stNumberInput input').forEach(function(el) {{
        el.style.background = inputBg;
        el.style.color = inputColor;
        el.style.webkitTextFillColor = inputColor;
    }});
}}, 400);
</script>
    """, unsafe_allow_html=True)


# ── Sidebar renderer ──────────────────────────────────────────────────────────
def render_sidebar(active: str = "home") -> str:
    theme = st.session_state.get("theme", "light")
    dark = theme == "dark"
    T = _tokens(dark)

    with st.sidebar:
        # Logo
        st.markdown(f"""
        <div style="padding:20px 16px 12px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:36px;height:36px;background:#3dbf94;border-radius:12px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:18px;flex-shrink:0;color:white;">🏥</div>
                <div>
                    <div style="font-size:1rem;font-weight:700;color:{T['text']};">MediAssist</div>
                    <div style="font-size:0.72rem;color:{T['text_muted']};margin-top:1px;">AI Health Platform</div>
                </div>
            </div>
        </div>
        <div style="height:1px;background:{T['border']};margin:0 16px 8px;"></div>
        """, unsafe_allow_html=True)

        # Language selectbox (hidden label)
        lang_choice = st.selectbox(
            "Language",
            options=["English", "العربية"],
            key="global_language",
            label_visibility="collapsed",
        )
        lang = "ar" if lang_choice == "العربية" else "en"

        # Section title
        st.markdown(
            f'<div style="font-size:10px;font-weight:700;letter-spacing:0.08em;'
            f'color:{T["text_muted"]};padding:12px 16px 4px;text-transform:uppercase;">'
            f'{"SERVICES" if lang == "en" else "الخدمات"}</div>',
            unsafe_allow_html=True,
        )

        # Navigation
        pages = [
            ("home",                   "🏠", "Home",                    "الرئيسية",                  "app"),
            ("chat",                   "🩺", "Health Q&A",              "الأسئلة الصحية",            "pages/chat"),
            ("calculators",            "⚖️", "Health Calculators",      "الحاسبات الصحية",           "pages/calculators"),
            ("lab_reader",             "🩸", "Lab Results Reader",      "قارئ نتائج المختبر",        "pages/lab_reader"),
            ("triage",                 "🚑", "Emergency Triage",        "الفرز الطارئ",              "pages/triage"),
            ("medicine_info",          "💊", "Medicine Info",           "معلومات الأدوية",           "pages/medicine_info"),
            ("food_nutrition_scanner", "🥗", "Food Nutrition Scanner",  "ماسح التغذية الغذائية",     "pages/food_nutrition_scanner"),
            ("nutrition_scanner",      "📸", "Nutrition Label Scanner", "ماسح ملصق القيم الغذائية", "pages/nutrition_scanner"),
        ]

        for key, icon, label_en, label_ar, page_path in pages:
            label = label_ar if lang == "ar" else label_en
            is_active = active == key
            if is_active:
                st.markdown(
                    f'<div style="background:#3dbf94;color:white;border-radius:12px;'
                    f'padding:9px 20px;margin:1px 8px;font-size:13px;font-weight:500;">'
                    f'{icon} {label}</div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
                    st.switch_page(f"{page_path}.py")

        # Footer — dark mode toggle
        st.markdown(
            f'<div style="height:1px;background:{T["border"]};margin:12px 16px 8px;"></div>',
            unsafe_allow_html=True,
        )
        toggle_icon = "☀️" if dark else "🌙"
        toggle_label = ("Light mode" if lang == "en" else "الوضع الفاتح") if dark else ("Dark mode" if lang == "en" else "الوضع الداكن")
        if st.button(f"{toggle_icon}  {toggle_label}", key="theme_toggle", use_container_width=True):
            st.session_state["theme"] = "light" if dark else "dark"
            st.rerun()

        st.markdown(
            f'<div style="font-size:0.7rem;color:{T["text_muted"]};text-align:center;padding:8px 0 16px;">'
            f'MediAssist v1.0 · Powered by Claude AI</div>',
            unsafe_allow_html=True,
        )

    return lang