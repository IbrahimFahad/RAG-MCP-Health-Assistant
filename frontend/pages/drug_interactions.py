import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from frontend.utils import apply_global_styles, render_sidebar, t
from app.services.drug_interactions.service import check_drug_interactions

st.set_page_config(
    page_title="Drug Interaction Checker | MediAssist",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_global_styles()
lang = render_sidebar(active="drug_interactions")

rtl = ' class="rtl"' if lang == "ar" else ""

# ── Extra CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.drug-tag {
    display: inline-block;
    background: var(--mint);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
    color: #2a9e78;
    margin: 3px;
}
.drug-tag.not-found {
    background: #fef2f2;
    color: #b91c1c;
}
.interaction-card {
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 10px;
    font-size: 13px;
    line-height: 1.7;
}
.severity-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 700;
    color: #fff;
    margin-left: 6px;
}
.serious-alert {
    background: #fef2f2;
    border: 2px solid #ef4444;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 16px;
}
.no-interaction {
    background: #e8f5f0;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div{rtl} style="margin-bottom:20px;">
  <div class="page-title">⚗️ {t("Drug Interaction Checker", "فاحص التفاعلات الدوائية", lang)}</div>
  <div class="page-subtitle">
    {t(
        "Enter 2 or more daily medications to check for potentially dangerous chemical interactions.",
        "أدخل دواءين أو أكثر من أدويتك اليومية للتحقق من التفاعلات الكيميائية الخطيرة المحتملة.",
        lang
    )}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Instructions card ────────────────────────────────────────────────────────
st.markdown(f"""
<div class="med-card" style="margin-bottom:18px;">
    <div style="font-size:12px;color:var(--text-mid);line-height:1.8;">
        {t(
            "💡 <strong>Tips:</strong> Use generic (scientific) drug names for best results "
            "(e.g. <em>Warfarin</em>, <em>Aspirin</em>, <em>Metformin</em>, <em>Ibuprofen</em>). "
            "Brand names may also work. Enter each medication in a separate field.",
            "💡 <strong>نصائح:</strong> استخدم الأسماء العلمية (الجنيسة) للأدوية للحصول على أفضل النتائج "
            "(مثل <em>وارفارين</em>، <em>أسبرين</em>، <em>ميتفورمين</em>، <em>إيبوبروفين</em>). "
            "الأسماء التجارية قد تعمل أيضاً. أدخل كل دواء في حقل منفصل.",
            lang
        )}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Resolve preset BEFORE widgets are instantiated ───────────────────────────
if "drug_preset" in st.session_state:
    preset = st.session_state.pop("drug_preset")
    for i, val in enumerate(preset):
        st.session_state[f"drug_{i}"] = val
    for i in range(len(preset), 5):
        st.session_state[f"drug_{i}"] = ""
    # No rerun needed — session state is set before widgets read it below

# ── Medication input fields ───────────────────────────────────────────────────
field_labels = [
    t("Medication 1 (required)", "الدواء الأول (مطلوب)", lang),
    t("Medication 2 (required)", "الدواء الثاني (مطلوب)", lang),
    t("Medication 3 (optional)", "الدواء الثالث (اختياري)", lang),
    t("Medication 4 (optional)", "الدواء الرابع (اختياري)", lang),
    t("Medication 5 (optional)", "الدواء الخامس (اختياري)", lang),
]
placeholders_en = ["e.g. Warfarin",   "e.g. Aspirin",    "e.g. Metformin", "e.g. Ibuprofen", "e.g. Lisinopril"]
placeholders_ar = ["مثال: وارفارين",  "مثال: أسبرين",   "مثال: ميتفورمين", "مثال: إيبوبروفين", "مثال: ليسينوبريل"]
placeholders = placeholders_ar if lang == "ar" else placeholders_en

col_a, col_b = st.columns(2, gap="small")
inputs = []
for i in range(5):
    col = col_a if i % 2 == 0 else col_b
    with col:
        val = st.text_input(field_labels[i], placeholder=placeholders[i], key=f"drug_{i}")
        inputs.append(val)

check_clicked = st.button(
    t("⚗️ Check Interactions", "⚗️ فحص التفاعلات", lang),
    use_container_width=True,
    type="primary",
)

# ── Quick example presets ─────────────────────────────────────────────────────
st.markdown(f"<small style='color:#9ca3af'>{t('Quick examples:', 'أمثلة سريعة:', lang)}</small>", unsafe_allow_html=True)
examples = (
    [("⚠️", "Warfarin + Aspirin", ["Warfarin", "Aspirin"]),
     ("💊", "Metformin + Ibuprofen", ["Metformin", "Ibuprofen"]),
     ("🧪", "Simvastatin + Amiodarone", ["Simvastatin", "Amiodarone"])]
    if lang == "en" else
    [("⚠️", "وارفارين + أسبرين", ["Warfarin", "Aspirin"]),
     ("💊", "ميتفورمين + إيبوبروفين", ["Metformin", "Ibuprofen"]),
     ("🧪", "سيمفاستاتين + أميودارون", ["Simvastatin", "Amiodarone"])]
)
ex_cols = st.columns(len(examples))
for i, (icon, label, drugs) in enumerate(examples):
    with ex_cols[i]:
        if st.button(f"{icon} {label}", key=f"ex_{i}", use_container_width=True):
            st.session_state["drug_preset"] = drugs
            st.rerun()

# ── Run check ────────────────────────────────────────────────────────────────
if check_clicked:
    drug_list = [v for v in inputs if v and v.strip()]

    if len(drug_list) < 2:
        st.warning(t("Please enter at least 2 medication names.", "يرجى إدخال اسمَي دواءين على الأقل.", lang))
    else:
        with st.spinner(t("Checking drug interactions via NIH RxNav…", "جارٍ فحص التفاعلات عبر NIH RxNav…", lang)):
            result = check_drug_interactions(drug_list, lang)

        if not result["success"]:
            st.error(result["error"])
            if result.get("drugs"):
                tags = "".join(
                    f'<span class="drug-tag {"not-found" if not d["found"] else ""}">'
                    f'{"✓" if d["found"] else "✗"} {d["name"]}</span>'
                    for d in result["drugs"]
                )
                st.markdown(f"<div style='margin-top:8px;'>{tags}</div>", unsafe_allow_html=True)
        else:
            # ── Identified drugs ─────────────────────────────────────────
            tags = "".join(
                f'<span class="drug-tag {"not-found" if not d["found"] else ""}">'
                f'{"✓" if d["found"] else "✗"} {d["name"]}</span>'
                for d in result["drugs"]
            )
            st.markdown(
                f'<div style="margin-bottom:14px;">'
                f'<span style="font-size:12px;color:var(--text-muted);">'
                f'{t("Identified medications:", "الأدوية المعرَّفة:", lang)}</span><br/>{tags}</div>',
                unsafe_allow_html=True,
            )

            if result.get("not_found"):
                st.info(t(
                    f"Note: {', '.join(result['not_found'])} could not be identified and were skipped.",
                    f"ملاحظة: تعذّر التعرف على {', '.join(result['not_found'])} وتم تجاهلها.",
                    lang,
                ))

            interactions = result["interactions"]

            # ── Serious alert banner ─────────────────────────────────────
            if result["has_serious"]:
                st.markdown(f"""
                <div class="serious-alert">
                    <div style="font-size:15px;font-weight:700;color:#b91c1c;">
                        🚨 {t("Serious Interaction Alert!", "تحذير: تفاعل دوائي خطير!", lang)}
                    </div>
                    <div style="font-size:13px;color:#7f1d1d;margin-top:6px;">
                        {t(
                            "One or more serious drug interactions were detected. "
                            "Please consult your doctor or pharmacist immediately before continuing these medications.",
                            "تم اكتشاف تفاعل دوائي خطير أو أكثر. "
                            "يُرجى استشارة طبيبك أو الصيدلاني فوراً قبل الاستمرار في تناول هذه الأدوية.",
                            lang
                        )}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ── Interaction list ─────────────────────────────────────────
            if not interactions:
                st.markdown(f"""
                <div class="no-interaction">
                    <div style="font-size:2rem;">✅</div>
                    <div style="font-size:15px;font-weight:600;color:#2a9e78;margin:8px 0;">
                        {t("No Known Interactions Found", "لا توجد تفاعلات معروفة", lang)}
                    </div>
                    <div style="font-size:12px;color:var(--text-muted);">
                        {t(
                            "The RxNav database found no documented interactions between these medications. "
                            "This does not guarantee complete safety — always consult your doctor.",
                            "لم تجد قاعدة بيانات RxNav أي تفاعلات موثّقة بين هذه الأدوية. "
                            "لا يعني ذلك السلامة المطلقة — استشر طبيبك دائماً.",
                            lang
                        )}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                count = result["interaction_count"]
                st.markdown(
                    f"#### {t(f'Found {count} interaction(s)', f'تم العثور على {count} تفاعل/تفاعلات', lang)}",
                )
                for ix in interactions:
                    sev_label = t(ix["label_en"], ix["label_ar"], lang)
                    st.markdown(f"""
                    <div class="interaction-card" style="background:{ix['bg']};border:1px solid {ix['border']};">
                        <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;flex-wrap:wrap;">
                            <span style="font-weight:700;color:{ix['color']};font-size:14px;">{ix['icon']}</span>
                            <span style="font-weight:600;color:var(--text);font-size:13px;">
                                {ix['drug1']} ↔ {ix['drug2']}
                            </span>
                            <span class="severity-badge" style="background:{ix['color']};">{sev_label}</span>
                        </div>
                        <div style="color:var(--text);font-size:13px;">{ix['description']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Disclaimer ───────────────────────────────────────────────
            st.markdown(f"""
            <div class="disclaimer">
                ⚠️ {t(
                    "This tool uses the NIH RxNav public database. Results are for informational purposes only "
                    "and do not constitute medical advice. Always consult a licensed doctor or pharmacist before "
                    "changing or combining medications.",
                    "يستخدم هذا الأداة قاعدة بيانات RxNav العامة التابعة لـ NIH. النتائج لأغراض إعلامية فقط "
                    "ولا تُعدّ استشارة طبية. استشر دائماً طبيباً مرخصاً أو صيدلانياً قبل تغيير الأدوية أو دمجها.",
                    lang
                )}
            </div>
            """, unsafe_allow_html=True)
