import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from frontend.utils import apply_global_styles, render_sidebar, t
from app.mcp_tools.health_calculators import calculate_bmi, calculate_bmr, calculate_ideal_weight

st.set_page_config(page_title="Calculators | MediAssist", page_icon="⚖️", layout="wide", initial_sidebar_state="expanded")
apply_global_styles()
lang = render_sidebar(active="calculators")

st.markdown(f'<div class="page-title">⚖️ {t("Health Calculators", "الحاسبات الصحية", lang)}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-subtitle">{t("Calculate your health metrics instantly.", "احسب مقاييسك الصحية فوراً.", lang)}</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "⚖️ " + t("BMI", "مؤشر كتلة الجسم", lang),
    "🔥 " + t("Daily Calories", "السعرات اليومية", lang),
    "📏 " + t("Ideal Weight", "الوزن المثالي", lang),
])

# ── Tab 1: BMI ────────────────────────────────────────────────────────────────
with tab1:
    st.markdown(f"#### {t('Body Mass Index (BMI)', 'مؤشر كتلة الجسم', lang)}")
    c1, c2 = st.columns(2)
    weight = c1.number_input(t("Weight (kg)", "الوزن (كغ)", lang), min_value=1.0, max_value=300.0, value=70.0, step=0.5)
    height = c2.number_input(t("Height (cm)", "الطول (سم)", lang), min_value=50.0, max_value=250.0, value=170.0, step=0.5)

    if st.button(t("Calculate BMI", "احسب مؤشر كتلة الجسم", lang), type="primary", key="calc_bmi"):
        result = calculate_bmi(weight, height)
        if "error" in result:
            st.error(result["error"])
        else:
            bmi = result["bmi"]
            category = result["category"]
            color_map = {
                "Underweight": "#185fa5",
                "Normal weight": "#2a9e78",
                "Overweight": "#854f0b",
                "Obese": "#a32d2d",
            }
            color = color_map.get(category, "var(--text-muted)")
            cat_ar = {"Underweight": "نقص الوزن", "Normal weight": "وزن طبيعي",
                      "Overweight": "زيادة وزن", "Obese": "سمنة"}.get(category, category)
            bmi_pos = max(2, min(98, (float(bmi) - 10) / 35 * 100))
            st.markdown(f"""
<div style="background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;margin:12px 0;">
    <div style="text-align:center;margin-bottom:20px;">
        <div style="font-size:48px;font-weight:700;color:{color};line-height:1;">{bmi}</div>
        <div style="font-size:1rem;font-weight:600;color:{color};margin-top:4px;">{t(category, cat_ar, lang)}</div>
        <div style="font-size:0.82rem;color:var(--text-muted);margin-top:2px;">{t("Healthy range: 18.5–24.9","النطاق الصحي: 18.5–24.9",lang)}</div>
    </div>
    <div style="margin-bottom:6px;">
        <div style="display:flex;height:12px;border-radius:6px;overflow:hidden;">
            <div style="width:24%;background:#185fa5;"></div>
            <div style="width:18%;background:#2a9e78;"></div>
            <div style="width:14%;background:#854f0b;"></div>
            <div style="width:44%;background:#a32d2d;"></div>
        </div>
        <div style="position:relative;height:14px;margin-top:2px;">
            <div style="position:absolute;left:{bmi_pos:.1f}%;transform:translateX(-50%);
                        width:0;height:0;border-left:6px solid transparent;
                        border-right:6px solid transparent;border-top:10px solid {color};"></div>
        </div>
    </div>
    <div style="display:flex;justify-content:space-between;font-size:10px;color:var(--text-muted);">
        <span style="color:#185fa5;text-align:left;">{t("Underweight","نقص الوزن",lang)}<br>&lt;18.5</span>
        <span style="color:#2a9e78;text-align:center;">{t("Normal","طبيعي",lang)}<br>18.5–24.9</span>
        <span style="color:#854f0b;text-align:center;">{t("Overweight","زيادة وزن",lang)}<br>25–29.9</span>
        <span style="color:#a32d2d;text-align:right;">{t("Obese","سمنة",lang)}<br>≥30</span>
    </div>
</div>
<div style="background:{color}18;border-left:4px solid {color};padding:12px 16px;border-radius:6px;margin-top:4px;">
    {result["advice"]}
</div>
""", unsafe_allow_html=True)

# ── Tab 2: BMR / Calories ─────────────────────────────────────────────────────
with tab2:
    st.markdown(f"#### {t('Daily Calorie Needs (BMR)', 'احتياجاتك اليومية من السعرات', lang)}")
    c1, c2, c3 = st.columns(3)
    w2 = c1.number_input(t("Weight (kg)", "الوزن (كغ)", lang), min_value=1.0, max_value=300.0, value=70.0, step=0.5, key="w2")
    h2 = c2.number_input(t("Height (cm)", "الطول (سم)", lang), min_value=50.0, max_value=250.0, value=170.0, step=0.5, key="h2")
    age = c3.number_input(t("Age (years)", "العمر (سنة)", lang), min_value=1, max_value=120, value=25, key="age")

    c4, c5 = st.columns(2)
    gender_label = c4.selectbox(t("Gender", "الجنس", lang), [t("Male", "ذكر", lang), t("Female", "أنثى", lang)], key="gender")
    gender = "male" if gender_label in ("Male", "ذكر") else "female"

    activity_map = {
        t("Sedentary (no exercise)", "خامل (بدون رياضة)", lang): "sedentary",
        t("Light (1-3 days/week)", "خفيف (1-3 أيام/أسبوع)", lang): "light",
        t("Moderate (3-5 days/week)", "متوسط (3-5 أيام/أسبوع)", lang): "moderate",
        t("Active (6-7 days/week)", "نشيط (6-7 أيام/أسبوع)", lang): "active",
        t("Very Active (athlete)", "نشيط جداً (رياضي)", lang): "very_active",
    }
    activity_label = c5.selectbox(t("Activity Level", "مستوى النشاط", lang), list(activity_map.keys()), index=2, key="activity")

    if st.button(t("Calculate Calories", "احسب السعرات", lang), type="primary", key="calc_bmr"):
        result = calculate_bmr(w2, h2, age, gender, activity_map[activity_label])
        if "error" in result:
            st.error(result["error"])
        else:
            r1, r2, r3, r4 = st.columns(4)
            r1.metric(t("BMR", "معدل الأيض", lang), f"{result['bmr']} kcal")
            r2.metric(t("Daily Need", "الاحتياج اليومي", lang), f"{result['daily_calories']} kcal")
            r3.metric(t("To Lose Weight", "لخسارة الوزن", lang), f"{result['to_lose_weight']} kcal")
            r4.metric(t("To Gain Weight", "لزيادة الوزن", lang), f"{result['to_gain_weight']} kcal")
            st.info(t("💡 A deficit of 500 kcal/day leads to ~0.5 kg weight loss per week.",
                      "💡 عجز 500 سعرة يومياً يؤدي إلى فقدان ~0.5 كغ أسبوعياً.", lang))

# ── Tab 3: Ideal Weight ───────────────────────────────────────────────────────
with tab3:
    st.markdown(f"#### {t('Ideal Body Weight (Devine Formula)', 'الوزن المثالي (معادلة ديفاين)', lang)}")
    c1, c2 = st.columns(2)
    h3 = c1.number_input(t("Height (cm)", "الطول (سم)", lang), min_value=100.0, max_value=250.0, value=170.0, step=0.5, key="h3")
    g3_label = c2.selectbox(t("Gender", "الجنس", lang), [t("Male", "ذكر", lang), t("Female", "أنثى", lang)], key="g3")
    g3 = "male" if g3_label in ("Male", "ذكر") else "female"

    if st.button(t("Calculate Ideal Weight", "احسب الوزن المثالي", lang), type="primary", key="calc_ibw"):
        result = calculate_ideal_weight(h3, g3)
        if "error" in result:
            st.error(result["error"])
        else:
            r1, r2 = st.columns(2)
            r1.metric(t("Ideal Weight (kg)", "الوزن المثالي (كغ)", lang), f"{result['ideal_weight_kg']} kg")
            r2.metric(t("Ideal Weight (lbs)", "الوزن المثالي (رطل)", lang), f"{result['ideal_weight_lbs']} lbs")
            st.caption(f"ℹ️ {result['note']}")