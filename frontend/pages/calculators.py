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
            color = {"Underweight": "#3b82f6", "Normal weight": "#22c55e", "Overweight": "#f59e0b", "Obese": "#ef4444"}.get(category, "#64748b")
            r1, r2, r3 = st.columns(3)
            r1.metric(t("Your BMI", "مؤشرك", lang), bmi)
            r2.metric(t("Category", "التصنيف", lang), category)
            r3.metric(t("Healthy range", "النطاق الصحي", lang), "18.5 – 24.9")
            st.markdown(f'<div style="background:{color}15;border-left:4px solid {color};padding:12px 16px;border-radius:6px;margin-top:12px;">{result["advice"]}</div>', unsafe_allow_html=True)

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