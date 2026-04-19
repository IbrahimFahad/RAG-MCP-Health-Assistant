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

rtl = ' class="rtl"' if lang == "ar" else ""

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(120deg,#3dbf94 0%,#2a8fa8 100%);
            border-radius:16px;padding:28px 32px;margin-bottom:20px;
            display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;">
    <div{rtl}>
        <div style="font-size:11px;font-weight:700;letter-spacing:0.1em;color:rgba(255,255,255,0.75);
                    text-transform:uppercase;margin-bottom:6px;">
            {"AI Health Platform" if lang == "en" else "منصة الصحة الذكية"}
        </div>
        <h1 style="font-size:1.8rem;font-weight:700;color:white;margin:0 0 8px;">
            {"MediAssist" if lang == "en" else "ميدي أسيست"}
        </h1>
        <p style="font-size:0.95rem;color:rgba(255,255,255,0.85);margin:0 0 18px;max-width:480px;">
            {"Your AI-powered health companion — trusted answers in Arabic & English"
             if lang == "en" else
             "مساعدك الصحي الذكي — إجابات موثوقة بالعربية والإنجليزية"}
        </p>
        <div style="display:flex;gap:24px;flex-wrap:wrap;">
            <div>
                <div style="font-size:1.3rem;font-weight:700;color:#f7f7f7;">7</div>
                <div style="font-size:10px;color:rgba(255,255,255,0.7);">{"AI Services" if lang == "en" else "خدمات ذكاء اصطناعي"}</div>
            </div>
            <div>
                <div style="font-size:1.3rem;font-weight:700;color:#f7f7f7;">2</div>
                <div style="font-size:10px;color:rgba(255,255,255,0.7);">{"Languages" if lang == "en" else "لغتان"}</div>
            </div>
            <div>
                <div style="font-size:1.3rem;font-weight:700;color:#f7f7f7;">Claude AI</div>
                <div style="font-size:10px;color:rgba(255,255,255,0.7);">{"Powered by Anthropic" if lang == "en" else "مدعوم بـ Anthropic"}</div>
            </div>
        </div>
    </div>
    <div style="font-size:5rem;opacity:0.25;user-select:none;">🏥</div>
</div>
""", unsafe_allow_html=True)

# ── Card helper ───────────────────────────────────────────────────────────────
def _card(icon, icon_bg, title, desc, badge_html, coming=False):
    opacity = "opacity:0.7;" if coming else ""
    border  = "border:1.5px dashed rgba(61,191,148,0.25);" if coming else "border:1px solid rgba(60,150,110,0.12);"
    return f"""
    <div style="background:var(--card);border-radius:16px;{border}padding:20px 18px;
                height:100%;{opacity}position:relative;transition:transform 0.15s,border-color 0.15s;
                cursor:{'default' if coming else 'pointer'};">
        <div style="width:40px;height:40px;background:{icon_bg};border-radius:10px;
                    display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:12px;">
            {icon}
        </div>
        <div style="font-size:13px;font-weight:600;color:var(--text);margin-bottom:6px;">{title}</div>
        <div style="font-size:12px;color:var(--text-mid);line-height:1.6;margin-bottom:12px;">{desc}</div>
        {badge_html}
    </div>"""

badge_ok   = '<span style="background:#e8f5f0;color:#2a9e78;padding:3px 10px;border-radius:20px;font-size:9px;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">AVAILABLE</span>'
badge_soon = '<span style="background:#e8f5f0;color:#8aab9f;padding:3px 10px;border-radius:20px;font-size:9px;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">COMING SOON</span>'

if lang == "ar":
    badge_ok   = '<span style="background:#e8f5f0;color:#2a9e78;padding:3px 10px;border-radius:20px;font-size:9px;font-weight:700;">متاح</span>'
    badge_soon = '<span style="background:#e8f5f0;color:#8aab9f;padding:3px 10px;border-radius:20px;font-size:9px;font-weight:700;">قريباً</span>'

# ── Row 1 ─────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3, gap="small")
with c1:
    st.markdown(_card("🩺","#ddeef8",
        t("Health Q&A","الأسئلة الصحية",lang),
        t("Ask any health question in Arabic or English. Powered by AI + trusted medical sources.",
          "اسأل أي سؤال صحي. مدعوم بالذكاء الاصطناعي ومصادر طبية موثوقة.",lang),
        badge_ok), unsafe_allow_html=True)
    if st.button("🩺 "+t("Open","فتح",lang), key="btn_chat", use_container_width=True):
        st.switch_page("pages/chat.py")

with c2:
    st.markdown(_card("⚖️","#e8f8ee",
        t("Health Calculators","الحاسبات الصحية",lang),
        t("Calculate BMI, daily calorie needs, and ideal body weight instantly.",
          "احسب مؤشر كتلة الجسم والسعرات الحرارية اليومية والوزن المثالي.",lang),
        badge_ok), unsafe_allow_html=True)
    if st.button("⚖️ "+t("Open","فتح",lang), key="btn_calc", use_container_width=True):
        st.switch_page("pages/calculators.py")

with c3:
    st.markdown(_card("🩸","#ede8fb",
        t("Lab Results Reader","قارئ نتائج المختبر",lang),
        t("Upload your blood test PDF — get a plain-language explanation of every value.",
          "ارفع ملف PDF لنتائج الدم واحصل على شرح مبسط لكل قيمة.",lang),
        badge_ok), unsafe_allow_html=True)
    if st.button("🩸 "+t("Open","فتح",lang), key="btn_lab", use_container_width=True):
        st.switch_page("pages/lab_reader.py")

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── Row 2 ─────────────────────────────────────────────────────────────────────
c4, c5, c6 = st.columns(3, gap="small")
with c4:
    st.markdown(_card("🚑","#fdeaea",
        t("Emergency Triage","الفرز الطارئ",lang),
        t("Answer guided yes/no questions — find out how urgently you need medical care.",
          "أجب على أسئلة موجّهة لمعرفة مدى إلحاح حاجتك للرعاية الطبية.",lang),
        badge_ok), unsafe_allow_html=True)
    if st.button("🚑 "+t("Open","فتح",lang), key="btn_triage", use_container_width=True):
        st.switch_page("pages/triage.py")

with c5:
    st.markdown(_card("💊","#fdeaf0",
        t("Medicine Info","معلومات الأدوية",lang),
        t("Ask about dosage, side effects, and drug interactions via AI chat.",
          "اسأل عن الجرعة والآثار الجانبية والتفاعلات عبر الدردشة الذكية.",lang),
        badge_ok), unsafe_allow_html=True)
    if st.button("💊 "+t("Open","فتح",lang), key="btn_med", use_container_width=True):
        st.switch_page("pages/medicine_info.py")

with c6:
    st.markdown(_card("🥗","#e8f8ee",
        t("Food Nutrition Scanner","ماسح التغذية الغذائية",lang),
        t("Type any food or meal — get a detailed breakdown of calories, macros & health tips.",
          "أدخل أي طعام أو وجبة للحصول على تحليل غذائي مفصّل.",lang),
        badge_ok), unsafe_allow_html=True)
    if st.button("🥗 "+t("Open","فتح",lang), key="btn_food", use_container_width=True):
        st.switch_page("pages/food_nutrition_scanner.py")

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── Row 3 ─────────────────────────────────────────────────────────────────────
c7, c8, c9 = st.columns(3, gap="small")
with c7:
    st.markdown(_card("📸","#fef6e0",
        t("Nutrition Label Scanner","ماسح ملصق القيم الغذائية",lang),
        t("Photograph a food label — AI reads every value, then chat about your diet.",
          "صوّر ملصق القيم الغذائية — يقرأ الذكاء الاصطناعي كل القيم ثم تحادثه.",lang),
        badge_ok), unsafe_allow_html=True)
    if st.button("📸 "+t("Open","فتح",lang), key="btn_label", use_container_width=True):
        st.switch_page("pages/nutrition_scanner.py")

with c8:
    st.markdown(_card("🧬","#e8f5f0",
        t("Coming Soon","قريباً",lang),
        t("A new health service is on the way. Stay tuned!",
          "خدمة صحية جديدة قادمة قريباً. ترقّبوا!",lang),
        badge_soon, coming=True), unsafe_allow_html=True)
    st.button("🔒 "+t("Coming Soon","قريباً",lang), key="btn_cs1", use_container_width=True, disabled=True)

with c9:
    st.markdown(_card("🔬","#e8f5f0",
        t("Coming Soon","قريباً",lang),
        t("A new health service is on the way. Stay tuned!",
          "خدمة صحية جديدة قادمة قريباً. ترقّبوا!",lang),
        badge_soon, coming=True), unsafe_allow_html=True)
    st.button("🔒 "+t("Coming Soon","قريباً",lang), key="btn_cs2", use_container_width=True, disabled=True)