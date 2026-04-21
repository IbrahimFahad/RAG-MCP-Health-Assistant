import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from frontend.utils import apply_global_styles, render_sidebar, t
from app.services.symptom_checker.service import check_symptoms

st.set_page_config(
    page_title="Symptom Checker | MediAssist",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_global_styles()
lang = render_sidebar(active="symptom_checker")

rtl = ' class="rtl"' if lang == "ar" else ""

# ── Extra CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.triage-banner {
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 16px;
}
.condition-card {
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 8px;
    border: 1px solid var(--border);
    background: var(--card);
    display: flex;
    align-items: center;
    gap: 14px;
}
.prob-bar-wrap {
    flex: 1;
}
.prob-bar-bg {
    background: var(--mint);
    border-radius: 6px;
    height: 7px;
    width: 100%;
    overflow: hidden;
}
.prob-bar-fill {
    height: 7px;
    border-radius: 6px;
    background: linear-gradient(90deg, #3dbf94, #2a8fa8);
}
.prob-label {
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 3px;
}
.explanation-box {
    background: var(--mint);
    border-radius: 14px;
    padding: 16px 18px;
    font-size: 13px;
    color: var(--text);
    line-height: 1.75;
    margin-bottom: 16px;
    border-left: 3px solid #3dbf94;
}
.evidence-chip {
    display: inline-block;
    background: #e8f5f0;
    color: #2a9e78;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
    margin: 3px;
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div{rtl} style="margin-bottom:20px;">
  <div class="page-title">🔍 {t("Symptom Checker", "مدقق الأعراض", lang)}</div>
  <div class="page-subtitle">
    {t(
        "Describe your symptoms and get a list of possible conditions with urgency guidance — powered by Claude AI.",
        "صف أعراضك واحصل على قائمة بالحالات المحتملة مع توجيهات حول الإلحاح — مدعوم بـ Claude AI.",
        lang
    )}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Info card ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="med-card" style="margin-bottom:18px;">
    <div style="font-size:12px;color:var(--text-mid);line-height:1.8;">
        {t(
            "💡 <strong>How it works:</strong> Enter your symptoms in plain language "
            "(e.g. <em>'I have a headache, fever, and feel very tired'</em>). "
            "Claude AI analyzes your symptoms, identifies the most likely conditions, "
            "assesses urgency, and explains everything in simple terms.",
            "💡 <strong>كيف يعمل:</strong> أدخل أعراضك بلغة عادية "
            "(مثل: <em>'لدي صداع وحمى وأشعر بتعب شديد'</em>). "
            "يحلل Claude AI أعراضك ويحدد الحالات الأكثر احتمالاً "
            "ويقيّم مستوى الإلحاح ويشرح كل شيء بأسلوب مبسط.",
            lang
        )}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Resolve preset BEFORE widgets are instantiated ───────────────────────────
if "symptom_preset" in st.session_state:
    st.session_state["symptoms_text"] = st.session_state.pop("symptom_preset")

# ── Input form ───────────────────────────────────────────────────────────────
col_a, col_b = st.columns([2, 1], gap="small")

with col_a:
    symptoms_input = st.text_area(
        t("Describe your symptoms *", "صف أعراضك *", lang),
        placeholder=t(
            "e.g. I have a severe headache, high fever, stiff neck, and sensitivity to light since yesterday.",
            "مثال: لدي صداع شديد وحمى مرتفعة وتصلب في الرقبة وحساسية للضوء منذ أمس.",
            lang,
        ),
        height=110,
        key="symptoms_text",
    )

with col_b:
    age_input = st.number_input(
        t("Age", "العمر", lang),
        min_value=1, max_value=130, value=30, step=1,
        key="patient_age",
    )
    sex_options = (
        ["Male", "Female"] if lang == "en" else ["ذكر", "أنثى"]
    )
    sex_choice = st.selectbox(
        t("Sex", "الجنس", lang),
        options=sex_options,
        key="patient_sex",
    )

sex_value = "male" if sex_choice in ("Male", "ذكر") else "female"

check_clicked = st.button(
    t("🔍 Check Symptoms", "🔍 تحقق من الأعراض", lang),
    use_container_width=True,
    type="primary",
)

# ── Quick example prompts ─────────────────────────────────────────────────────
st.markdown(
    f"<small style='color:#9ca3af'>{t('Quick examples:', 'أمثلة سريعة:', lang)}</small>",
    unsafe_allow_html=True,
)
examples_en = [
    ("🤒", "Flu-like", "I have a fever, body aches, sore throat, and runny nose for 2 days."),
    ("💔", "Chest pain", "I have chest pain, shortness of breath, and left arm tingling."),
    ("🤢", "Stomach", "I have stomach pain, nausea, and diarrhea after eating."),
]
examples_ar = [
    ("🤒", "أعراض الإنفلونزا", "لدي حمى وآلام في الجسم والتهاب في الحلق وسيلان الأنف منذ يومين."),
    ("💔", "ألم الصدر", "لدي ألم في الصدر وضيق في التنفس وتنميل في الذراع الأيسر."),
    ("🤢", "مشاكل المعدة", "لدي ألم في المعدة وغثيان وإسهال بعد الأكل."),
]
examples = examples_ar if lang == "ar" else examples_en

ex_cols = st.columns(len(examples))
for i, (icon, label, text) in enumerate(examples):
    with ex_cols[i]:
        if st.button(f"{icon} {label}", key=f"ex_{i}", use_container_width=True):
            st.session_state["symptom_preset"] = text
            st.rerun()  # rerun so preset is applied before text_area renders

# ── Run check ────────────────────────────────────────────────────────────────
if check_clicked:
    text = st.session_state.get("symptoms_text", "").strip()

    if not text:
        st.warning(t(
            "Please describe your symptoms before checking.",
            "يرجى وصف أعراضك قبل التحقق.",
            lang,
        ))
    else:
        with st.spinner(t(
            "Analyzing symptoms via Claude AI…",
            "جارٍ تحليل الأعراض عبر Claude AI…",
            lang,
        )):
            result = check_symptoms(
                symptoms_text=text,
                age=int(age_input),
                sex=sex_value,
                lang=lang,
            )

        if not result["success"]:
            st.error(result["error"])
        else:
            cfg = result["triage_config"]
            triage_level = result["triage_level"]

            # ── Triage banner ────────────────────────────────────────────
            triage_label = t(cfg["label_en"], cfg["label_ar"], lang)
            triage_advice = t(cfg["advice_en"], cfg["advice_ar"], lang)
            is_emergency = triage_level == "emergency"

            st.markdown(f"""
            <div class="triage-banner" style="background:{cfg['bg']};border:2px solid {cfg['border']};">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                    <span style="font-size:22px;">{cfg['icon']}</span>
                    <span style="font-size:15px;font-weight:700;color:{cfg['color']};">{triage_label}</span>
                </div>
                <div style="font-size:13px;color:{cfg['color']};opacity:0.85;">{triage_advice}</div>
            </div>
            """, unsafe_allow_html=True)

            if is_emergency:
                st.markdown(f"""
                <div style="background:#fef2f2;border:2px solid #ef4444;border-radius:14px;
                            padding:14px 18px;margin-bottom:16px;">
                    <strong style="color:#b91c1c;">
                        {t(
                            "⚠️ These symptoms may indicate a serious or life-threatening condition. "
                            "Seek emergency medical care immediately.",
                            "⚠️ قد تشير هذه الأعراض إلى حالة خطيرة أو مهددة للحياة. "
                            "اطلب رعاية طبية طارئة فوراً.",
                            lang
                        )}
                    </strong>
                </div>
                """, unsafe_allow_html=True)

            # ── Claude explanation ────────────────────────────────────────
            if result.get("explanation"):
                st.markdown(
                    f'<div class="explanation-box">💬 {result["explanation"]}</div>',
                    unsafe_allow_html=True,
                )

            # ── Conditions list ──────────────────────────────────────────
            conditions = result["conditions"]
            if conditions:
                st.markdown(
                    f"#### {t('Possible Conditions', 'الحالات المحتملة', lang)} "
                    f"<small style='color:var(--text-muted);font-size:12px;font-weight:400;'>"
                    f"({t('ranked by likelihood', 'مرتبة حسب الاحتمالية', lang)})</small>",
                    unsafe_allow_html=True,
                )
                for i, cond in enumerate(conditions):
                    name = cond.get("name", "Unknown")
                    prob = cond.get("probability", 0)
                    pct = round(prob * 100, 1)
                    severity = cond.get("severity", "")
                    icd = cond.get("icd10_code", "")

                    severity_color = {"mild": "#10b981", "moderate": "#f59e0b", "severe": "#ef4444"}.get(severity, "#6b7280")
                    rank_color = ["#3dbf94", "#2a8fa8", "#6b7280", "#8aab9f", "#a3b8b0", "#bfcfcc"][min(i, 5)]

                    icd_badge = f'<span style="font-size:10px;color:var(--text-muted);margin-left:6px;">ICD: {icd}</span>' if icd else ""
                    sev_badge = (
                        f'<span style="font-size:10px;color:{severity_color};font-weight:600;'
                        f'background:{severity_color}18;padding:2px 7px;border-radius:10px;margin-left:4px;">'
                        f'{severity.capitalize()}</span>'
                        if severity else ""
                    )

                    st.markdown(f"""
                    <div class="condition-card">
                        <div style="width:28px;height:28px;background:{rank_color}18;border-radius:50%;
                                    display:flex;align-items:center;justify-content:center;
                                    font-size:12px;font-weight:700;color:{rank_color};flex-shrink:0;">
                            {i + 1}
                        </div>
                        <div style="flex:1;min-width:0;">
                            <div style="font-size:13px;font-weight:600;color:var(--text);
                                        display:flex;align-items:center;flex-wrap:wrap;gap:4px;margin-bottom:6px;">
                                {name}{sev_badge}{icd_badge}
                            </div>
                            <div class="prob-bar-bg">
                                <div class="prob-bar-fill" style="width:{min(pct, 100)}%;"></div>
                            </div>
                            <div class="prob-label">{t('Probability', 'الاحتمالية', lang)}: {pct}%</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Red flags + condition count chips ────────────────────────
            chips_html = f'<span class="evidence-chip">✓ {len(conditions)} {t("condition(s) found", "حالة/حالات وُجدت", lang)}</span>'
            for flag in result.get("red_flags", []):
                chips_html += f'<span class="evidence-chip" style="background:#fef2f2;color:#b91c1c;">⚠ {flag}</span>'
            st.markdown(f'<div style="margin-top:8px;">{chips_html}</div>', unsafe_allow_html=True)

            # ── Disclaimer ───────────────────────────────────────────────
            st.markdown(f"""
            <div class="disclaimer">
                ⚠️ {t(
                    "This tool uses Claude AI for symptom analysis. Results are for informational and "
                    "screening purposes only — they do not constitute a medical diagnosis. "
                    "Always consult a qualified doctor for any health concern.",
                    "تستخدم هذه الأداة Claude AI لتحليل الأعراض. النتائج لأغراض إعلامية وفحصية فقط "
                    "— ولا تُعدّ تشخيصاً طبياً. استشر دائماً طبيباً مؤهلاً لأي مخاوف صحية.",
                    lang
                )}
            </div>
            """, unsafe_allow_html=True)
