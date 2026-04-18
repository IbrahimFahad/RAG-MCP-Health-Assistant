import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(override=True)

"""
Food Nutrition Scanner — Streamlit Page
Plugs into the MediAssist dashboard.
"""

import streamlit as st
from frontend.utils import apply_global_styles, render_sidebar, t
from app.services.food_nutrition_scanner.service import (
    scan_food,
    get_category_emoji,
    get_calorie_level,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Food Nutrition Scanner | MediAssist",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_global_styles()
lang = render_sidebar(active="food_nutrition_scanner")

# ── Custom CSS for nutrition cards ───────────────────────────────────────────
st.markdown("""
<style>
.scan-header {
    text-align: center;
    padding: 1.5rem 0 1rem;
}
.scan-header h1 {
    font-size: 2rem;
    margin-bottom: 0.25rem;
}
.scan-header p {
    opacity: 0.7;
    font-size: 1.05rem;
}
.nutrition-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}
.macro-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.75rem;
    margin: 1rem 0;
}
.macro-item {
    background: #f0f4f8;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.macro-item .value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #0a2540;
}
.macro-item .label {
    font-size: 0.82rem;
    color: #6b7280;
    margin-top: 2px;
}
.calorie-badge {
    display: inline-block;
    padding: 0.35rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9rem;
    color: #fff;
}
.micro-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 0.5rem;
}
.micro-table td {
    padding: 0.45rem 0.75rem;
    border-bottom: 1px solid #f0f0f0;
    font-size: 0.92rem;
}
.micro-table td:first-child {
    color: #6b7280;
}
.micro-table td:last-child {
    font-weight: 600;
    text-align: right;
    color: #0a2540;
}
.health-note {
    background: #ecfdf5;
    border-left: 3px solid #22c55e;
    padding: 0.6rem 1rem;
    margin: 0.4rem 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.92rem;
    color: #065f46;
}
.rtl .health-note {
    border-left: none;
    border-right: 3px solid #22c55e;
    border-radius: 8px 0 0 8px;
}
.disclaimer-box {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #92400e;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
rtl_class = ' class="rtl"' if lang == "ar" else ""

st.markdown(f"""
<div{rtl_class}>
<div class="scan-header">
    <h1>🥗 {t("Food Nutrition Scanner", "ماسح التغذية الغذائية", lang)}</h1>
    <p>{t(
        "Enter any food or meal to get a detailed nutritional breakdown.",
        "أدخل أي طعام أو وجبة للحصول على تحليل غذائي مفصّل.",
        lang
    )}</p>
</div>
</div>
""", unsafe_allow_html=True)

# ── Input ────────────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([4, 1])
with col_input:
    food_input = st.text_input(
        t("Describe the food or meal", "صف الطعام أو الوجبة", lang),
        placeholder=t(
            "e.g. grilled chicken breast with rice and salad",
            "مثال: صدر دجاج مشوي مع أرز وسلطة",
            lang,
        ),
        label_visibility="collapsed",
    )
with col_btn:
    scan_clicked = st.button(
        t("🔍 Scan", "🔍 فحص", lang),
        use_container_width=True,
        type="primary",
    )

# ── Quick examples ───────────────────────────────────────────────────────────
examples = (
    [
        ("🍌", "Banana"),
        ("🍳", "Two fried eggs with toast"),
        ("🥙", "Chicken shawarma wrap"),
        ("🍝", "Spaghetti Bolognese"),
    ]
    if lang == "en"
    else [
        ("🍌", "موزة"),
        ("🍳", "بيضتان مقليتان مع توست"),
        ("🥙", "شاورما دجاج بالخبز"),
        ("🍝", "معكرونة بولونيز"),
    ]
)

st.markdown(f"<small style='color:#9ca3af'>{t('Quick examples:', 'أمثلة سريعة:', lang)}</small>", unsafe_allow_html=True)
example_cols = st.columns(len(examples))
for i, (emoji, label) in enumerate(examples):
    with example_cols[i]:
        if st.button(f"{emoji} {label}", key=f"ex_{i}", use_container_width=True):
            st.session_state["food_input_override"] = label
            st.rerun()

# Handle example click
if "food_input_override" in st.session_state:
    food_input = st.session_state.pop("food_input_override")
    scan_clicked = True

# ── Scan & display ───────────────────────────────────────────────────────────
if scan_clicked and food_input:
    with st.spinner(t("Analyzing nutritional content…", "جارٍ تحليل المحتوى الغذائي…", lang)):
        result = scan_food(food_input)

    if not result["success"]:
        st.error(result["error"])
    else:
        n = result["nutrition"]
        macro = n.get("macronutrients", {})
        micro = n.get("micronutrients", {})
        cal_level = get_calorie_level(n.get("calories", 0))
        cat_emoji = get_category_emoji(n.get("category", "other"))
        is_rtl = lang == "ar"
        wrap_open = '<div class="rtl">' if is_rtl else "<div>"

        # ── Food title + calorie badge ───────────────────────────────────
        st.markdown(f"""
        {wrap_open}
        <div class="nutrition-card" style="text-align:center">
            <span style="font-size:2.5rem">{cat_emoji}</span>
            <h2 style="margin:0.25rem 0">{n.get("food_name", food_input)}</h2>
            <p style="color:#6b7280;margin:0 0 0.75rem">{t("Serving:", "الحصة:", lang)} {n.get("serving_size", "—")}</p>
            <span class="calorie-badge" style="background:{cal_level['color']}">
                {n.get("calories", 0)} {t("kcal", "سعرة", lang)} — {t(cal_level["label_en"], cal_level["label_ar"], lang)}
            </span>
        </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Macronutrients ───────────────────────────────────────────────
        st.markdown(f"#### {t('Macronutrients', 'العناصر الغذائية الكبرى', lang)}")
        macro_labels = {
            "protein_g": t("Protein", "بروتين", lang),
            "carbs_g": t("Carbs", "كربوهيدرات", lang),
            "fat_g": t("Fat", "دهون", lang),
            "fiber_g": t("Fiber", "ألياف", lang),
            "sugar_g": t("Sugar", "سكر", lang),
        }
        macro_html = f'{wrap_open}<div class="macro-grid">'
        for key, label in macro_labels.items():
            val = macro.get(key, 0)
            macro_html += f"""
            <div class="macro-item">
                <div class="value">{val}g</div>
                <div class="label">{label}</div>
            </div>"""
        macro_html += "</div></div>"
        st.markdown(macro_html, unsafe_allow_html=True)

        # ── Macronutrient bar chart ──────────────────────────────────────
        macro_chart_data = {
            t("Protein", "بروتين", lang): macro.get("protein_g", 0),
            t("Carbs", "كربوهيدرات", lang): macro.get("carbs_g", 0),
            t("Fat", "دهون", lang): macro.get("fat_g", 0),
        }
        st.bar_chart(macro_chart_data)

        # ── Micronutrients ───────────────────────────────────────────────
        st.markdown(f"#### {t('Micronutrients', 'العناصر الغذائية الدقيقة', lang)}")
        micro_labels = {
            "sodium_mg": (t("Sodium", "صوديوم", lang), "mg"),
            "potassium_mg": (t("Potassium", "بوتاسيوم", lang), "mg"),
            "calcium_mg": (t("Calcium", "كالسيوم", lang), "mg"),
            "iron_mg": (t("Iron", "حديد", lang), "mg"),
            "vitamin_c_mg": (t("Vitamin C", "فيتامين سي", lang), "mg"),
            "vitamin_a_iu": (t("Vitamin A", "فيتامين أ", lang), "IU"),
        }
        micro_html = f'{wrap_open}<table class="micro-table">'
        for key, (label, unit) in micro_labels.items():
            val = micro.get(key, 0)
            micro_html += f"<tr><td>{label}</td><td>{val} {unit}</td></tr>"
        micro_html += "</table></div>"
        st.markdown(micro_html, unsafe_allow_html=True)

        # ── Health notes ─────────────────────────────────────────────────
        notes = n.get("health_notes", [])
        if notes:
            st.markdown(f"#### {t('Health Notes', 'ملاحظات صحية', lang)}")
            for note in notes:
                cls = 'rtl' if is_rtl else ''
                st.markdown(
                    f'<div class="health-note {cls}">💡 {note}</div>',
                    unsafe_allow_html=True,
                )

        # ── Disclaimer ───────────────────────────────────────────────────
        st.markdown(
            f'<div class="disclaimer-box">⚠️ {result["disclaimer"]}</div>',
            unsafe_allow_html=True,
        )

        # ── Follow-up suggestions ────────────────────────────────────────
        followups = result.get("followups", [])
        if followups:
            st.markdown(f"#### {t('You might also ask', 'قد ترغب أيضًا بسؤال', lang)}")
            for fq in followups:
                st.markdown(f"- {fq}")

elif scan_clicked and not food_input:
    st.warning(t("Please enter a food or meal to scan.", "يرجى إدخال طعام أو وجبة للفحص.", lang))