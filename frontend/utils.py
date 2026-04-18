import streamlit as st

# ── Translation helper ────────────────────────────────────────────────────────
def t(en: str, ar: str, lang: str) -> str:
    return ar if lang == "ar" else en

# ── Global CSS ────────────────────────────────────────────────────────────────
def apply_global_styles():
    st.markdown("""
    <style>
    /* ── Base ── */
    [data-testid="stAppViewContainer"] {
        background: #f0f4f8;
    }
    [data-testid="stSidebar"] {
        background: #0a2540;
    }
    [data-testid="stSidebar"] * {
        color: #e8edf2 !important;
    }

    /* ── Hero ── */
    .hero-section {
        background: linear-gradient(135deg, #0a2540 0%, #1a4a7a 100%);
        border-radius: 16px;
        padding: 48px 40px;
        margin-bottom: 8px;
        color: white;
    }
    .hero-section h1 {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 12px;
        color: white !important;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #a8c8f0 !important;
        max-width: 600px;
    }

    /* ── Service Cards ── */
    .service-card {
        background: white;
        border-radius: 14px;
        padding: 28px 24px;
        margin-bottom: 8px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        min-height: 200px;
        transition: box-shadow 0.2s;
    }
    .service-card:hover {
        box-shadow: 0 6px 20px rgba(0,0,0,0.10);
    }
    .service-card .card-icon {
        font-size: 2.2rem;
        margin-bottom: 12px;
    }
    .service-card h3 {
        font-size: 1.1rem;
        font-weight: 600;
        color: #0a2540;
        margin-bottom: 8px;
    }
    .service-card p {
        font-size: 0.88rem;
        color: #64748b;
        line-height: 1.5;
        margin-bottom: 12px;
    }
    .service-card.coming-soon {
        opacity: 0.75;
    }

    /* ── Badges ── */
    .badge-available {
        background: #dcfce7;
        color: #166534;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-coming {
        background: #fef9c3;
        color: #854d0e;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* ── Sidebar nav items ── */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 4px;
        cursor: pointer;
        font-size: 0.95rem;
        color: #c8d8e8;
        transition: background 0.15s;
    }
    .nav-item:hover, .nav-item.active {
        background: #1a3a5c;
        color: white;
    }
    .nav-section-title {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #5a7a9a !important;
        padding: 16px 14px 4px;
        text-transform: uppercase;
    }

    /* ── RTL ── */
    .rtl { direction: rtl; text-align: right; }

    /* ── Page title ── */
    .page-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0a2540;
        margin-bottom: 4px;
    }
    .page-subtitle {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 24px;
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: white;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #e2e8f0;
    }

    /* Hide streamlit default elements */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


# ── Sidebar renderer ──────────────────────────────────────────────────────────
def render_sidebar(active: str = "home") -> str:
    """Renders the sidebar and returns the selected language ('en' or 'ar')."""

    with st.sidebar:
        # Logo / brand
        st.markdown("""
        <div style="padding: 20px 14px 8px;">
            <div style="font-size:1.5rem; font-weight:700; color:white;">🏥 MediAssist</div>
            <div style="font-size:0.78rem; color:#5a7a9a; margin-top:2px;">AI Health Platform</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Language toggle
        lang_choice = st.selectbox(
            "🌐",
            options=["English", "العربية"],
            key="global_language",
            label_visibility="collapsed"
        )
        lang = "ar" if lang_choice == "العربية" else "en"

        st.markdown(f'<div class="nav-section-title">{"SERVICES" if lang == "en" else "الخدمات"}</div>', unsafe_allow_html=True)

        # Navigation buttons
        pages = [
            ("home",          "🏠", "Home",                "الرئيسية",              "app"),
            ("chat",          "🩺", "Health Q&A",          "الأسئلة الصحية",        "pages/chat"),
            ("calculators",   "⚖️", "Health Calculators",  "الحاسبات الصحية",       "pages/calculators"),
            ("lab_reader",    "🩸", "Lab Results Reader",  "قارئ نتائج المختبر",    "pages/lab_reader"),
            ("triage",        "🚑", "Emergency Triage",    "الفرز الطارئ",          "pages/triage"),
            ("medicine_info",          "💊", "Medicine Info",             "معلومات الأدوية",              "pages/medicine_info"),
            ("food_nutrition_scanner", "🥗", "Food Nutrition Scanner",    "ماسح التغذية الغذائية",        "pages/food_nutrition_scanner"),
            ("nutrition_scanner",      "📸", "Nutrition Label Scanner",   "ماسح ملصق القيم الغذائية",    "pages/nutrition_scanner"),
        ]

        for key, icon, label_en, label_ar, page_path in pages:
            label = label_ar if lang == "ar" else label_en
            is_active = active == key
            style = "background:#1a3a5c; color:white;" if is_active else ""
            st.markdown(f'<div class="nav-item" style="{style}">{icon} {label}</div>', unsafe_allow_html=True)
            if not is_active:
                if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
                    st.switch_page(f"{page_path}.py")

        # Footer
        st.markdown("""
        <div style="position:absolute; bottom:20px; left:14px; right:14px;
                    font-size:0.72rem; color:#3a5a7a; text-align:center;">
            MediAssist v1.0 · College Project
        </div>
        """, unsafe_allow_html=True)

    return lang