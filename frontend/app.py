import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from frontend.utils import apply_global_styles, render_sidebar, t

st.set_page_config(
    page_title="MediAssist | منصة الصحة الذكية",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()

lang = render_sidebar(active="home")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-section">
    <div class="hero-content">
        <h1>{"🏥 MediAssist" if lang == "en" else "🏥 ميدي أسيست"}</h1>
        <p class="hero-subtitle">
            {"Your AI-powered health companion — trusted answers in Arabic & English"
             if lang == "en" else
             "مساعدك الصحي الذكي — إجابات موثوقة بالعربية والإنجليزية"}
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Service Cards ─────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="service-card available">
        <div class="card-icon">🩺</div>
        <h3>{"Health Q&A" if lang == "en" else "الأسئلة الصحية"}</h3>
        <p>{"Ask any health question in Arabic or English. Powered by AI + trusted medical sources."
            if lang == "en" else
            "اسأل أي سؤال صحي بالعربية أو الإنجليزية. مدعوم بالذكاء الاصطناعي ومصادر طبية موثوقة."}</p>
        <span class="badge-available">{"Available" if lang == "en" else "متاح"}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🩺 " + ("Open Health Q&A" if lang == "en" else "فتح الأسئلة الصحية"), use_container_width=True, key="btn_chat"):
        st.switch_page("pages/chat.py")

with col2:
    st.markdown(f"""
    <div class="service-card available">
        <div class="card-icon">⚖️</div>
        <h3>{"Health Calculators" if lang == "en" else "الحاسبات الصحية"}</h3>
        <p>{"Calculate BMI, daily calorie needs, and ideal body weight instantly."
            if lang == "en" else
            "احسب مؤشر كتلة الجسم والسعرات الحرارية اليومية والوزن المثالي فوراً."}</p>
        <span class="badge-available">{"Available" if lang == "en" else "متاح"}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⚖️ " + ("Open Calculators" if lang == "en" else "فتح الحاسبات"), use_container_width=True, key="btn_calc"):
        st.switch_page("pages/calculators.py")

with col3:
    st.markdown(f"""
    <div class="service-card coming-soon">
        <div class="card-icon">📸</div>
        <h3>{"Nutrition Scanner" if lang == "en" else "ماسح التغذية"}</h3>
        <p>{"Scan food nutrition labels and get instant AI-powered dietary feedback."
            if lang == "en" else
            "امسح ملصقات التغذية على الأطعمة واحصل على تغذية راجعة فورية."}</p>
        <span class="badge-coming">{"Coming Soon" if lang == "en" else "قريباً"}</span>
    </div>
    """, unsafe_allow_html=True)
    st.button("🔒 " + ("Coming Soon" if lang == "en" else "قريباً"), use_container_width=True, key="btn_nutrition", disabled=True)

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(f"""
    <div class="service-card available">
        <div class="card-icon">🩸</div>
        <h3>{"Lab Results Reader" if lang == "en" else "قارئ نتائج المختبر"}</h3>
        <p>{"Upload your blood test PDF and get a plain-language explanation of every value — normal ranges included."
            if lang == "en" else
            "ارفع ملف PDF لنتائج تحاليل الدم واحصل على شرح مبسط لكل قيمة مع المعدلات الطبيعية."}</p>
        <span class="badge-available">{"Available" if lang == "en" else "متاح"}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🩸 " + ("Open Lab Reader" if lang == "en" else "فتح قارئ المختبر"), use_container_width=True, key="btn_lab"):
        st.switch_page("pages/lab_reader.py")

with col5:
    st.markdown(f"""
    <div class="service-card available">
        <div class="card-icon">🚑</div>
        <h3>{"Emergency Triage" if lang == "en" else "الفرز الطارئ"}</h3>
        <p>{"Answer guided yes/no questions to find out how urgently you need medical care — from home management to call 911."
            if lang == "en" else
            "أجب على أسئلة موجّهة بنعم/لا لمعرفة مدى إلحاح حاجتك للرعاية الطبية — من الإدارة المنزلية إلى الاتصال بالطوارئ."}</p>
        <span class="badge-available">{"Available" if lang == "en" else "متاح"}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚑 " + ("Open Triage" if lang == "en" else "فتح الفرز الطارئ"), use_container_width=True, key="btn_triage"):
        st.switch_page("pages/triage.py")

with col6:
    st.markdown(f"""
    <div class="service-card available">
        <div class="card-icon">💊</div>
        <h3>{"Medicine Info" if lang == "en" else "معلومات الأدوية"}</h3>
        <p>{"Upload medicine leaflets or paste drug info, then ask questions about dosage, side effects, and interactions."
            if lang == "en" else
            "ارفع نشرات الأدوية أو الصق معلومات الدواء، ثم اسأل عن الجرعة والآثار الجانبية والتفاعلات."}</p>
        <span class="badge-available">{"Available" if lang == "en" else "متاح"}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("💊 " + ("Open Medicine Info" if lang == "en" else "فتح معلومات الأدوية"), use_container_width=True, key="btn_med"):
        st.switch_page("pages/medicine_info.py")

# ── Stats bar ─────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.divider()
s1, s2, s3, s4 = st.columns(4)
s1.metric("📚 " + ("Knowledge Base" if lang == "en" else "قاعدة المعرفة"), "110+ " + ("Chunks" if lang == "en" else "جزء"))
s2.metric("🌍 " + ("Languages" if lang == "en" else "اللغات"), "Arabic + English")
s3.metric("🔬 " + ("Medical Sources" if lang == "en" else "المصادر الطبية"), "WHO, NHS, NIH+")
s4.metric("🛠️ " + ("AI Tools" if lang == "en" else "أدوات الذكاء"), "7 MCP Tools")