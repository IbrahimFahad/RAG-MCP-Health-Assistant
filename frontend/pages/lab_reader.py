import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from frontend.utils import apply_global_styles, render_sidebar, t
from app.services.lab_reader import (
    extract_text_from_pdf,
    analyze_lab_results,
    get_status_color,
    get_status_emoji,
)

st.set_page_config(
    page_title="Lab Results Reader | MediAssist",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_global_styles()
lang = render_sidebar(active="lab_reader")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="page-title">🩸 {t("Lab Results Reader", "قارئ نتائج المختبر", lang)}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="page-subtitle">'
    f'{t("Upload your blood test PDF and get a plain-language explanation of every result.", "ارفع ملف PDF لنتائج تحاليل الدم واحصل على شرح مبسط لكل نتيجة.", lang)}'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Upload area ───────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    t("Upload Lab Report (PDF)", "ارفع تقرير المختبر (PDF)", lang),
    type=["pdf"],
    help=t(
        "Upload a PDF of your blood test or lab report. Max 10 MB.",
        "ارفع ملف PDF لتقرير الدم أو المختبر. الحد الأقصى 10 ميجابايت.",
        lang,
    ),
)

if uploaded:
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        analyze_clicked = st.button(
            "🔬 " + t("Analyze Results", "تحليل النتائج", lang),
            type="primary",
            use_container_width=True,
        )
    with col_info:
        st.caption(
            t(
                f"📄 File: **{uploaded.name}** · {uploaded.size // 1024} KB",
                f"📄 الملف: **{uploaded.name}** · {uploaded.size // 1024} كيلوبايت",
                lang,
            )
        )

    if analyze_clicked:
        with st.spinner(t("Reading your lab report...", "جاري قراءة تقرير المختبر...", lang)):
            raw_bytes = uploaded.read()
            pdf_text  = extract_text_from_pdf(raw_bytes)

        if not pdf_text.strip():
            st.error(
                t(
                    "Could not extract text from this PDF. Make sure it is a text-based (not scanned image) PDF.",
                    "تعذّر استخراج النص من هذا الملف. تأكد من أنه ملف PDF يحتوي على نص (وليس صورة ممسوحة).",
                    lang,
                )
            )
            st.stop()

        with st.spinner(t("Asking Claude to interpret your results...", "جاري طلب تفسير النتائج من كلود...", lang)):
            data = analyze_lab_results(pdf_text, language=lang)

        # ── Error from Claude ──────────────────────────────────────────────────
        if "error" in data:
            st.error(
                t(
                    f"⚠️ {data['error']}",
                    f"⚠️ {data['error']}",
                    lang,
                )
            )
            st.stop()

        # ── Urgent banner ──────────────────────────────────────────────────────
        if data.get("urgent"):
            st.markdown(
                f"""<div style="background:#fef2f2;border:2px solid #ef4444;border-radius:10px;
                             padding:16px 20px;margin-bottom:16px;">
                    <b style="color:#ef4444;font-size:1.05rem;">
                        🚨 {t("Some results may require urgent medical attention. Please consult your doctor immediately.",
                               "بعض النتائج قد تستلزم رعاية طبية عاجلة. يرجى استشارة طبيبك فوراً.", lang)}
                    </b>
                </div>""",
                unsafe_allow_html=True,
            )

        # ── Patient info ───────────────────────────────────────────────────────
        pinfo = data.get("patient_info", {})
        if pinfo.get("name") or pinfo.get("date"):
            pi_col1, pi_col2 = st.columns(2)
            if pinfo.get("name"):
                pi_col1.info(f"👤 {t('Patient', 'المريض', lang)}: **{pinfo['name']}**")
            if pinfo.get("date"):
                pi_col2.info(f"📅 {t('Date', 'التاريخ', lang)}: **{pinfo['date']}**")

        # ── Summary ────────────────────────────────────────────────────────────
        if data.get("summary"):
            st.markdown(
                f"""<div style="background:#f0f9ff;border-left:4px solid #3b82f6;
                             border-radius:6px;padding:14px 18px;margin-bottom:20px;">
                    <b style="color:#1e40af;">{t("Summary", "الملخص", lang)}</b><br>
                    <span style="color:#1e3a5f;">{data["summary"]}</span>
                </div>""",
                unsafe_allow_html=True,
            )

        # ── Results table ──────────────────────────────────────────────────────
        results = data.get("results", [])
        if not results:
            st.warning(t("No lab values found in this document.", "لم يتم العثور على قيم مختبرية في هذا المستند.", lang))
            st.stop()

        st.markdown(
            f"### 🧪 {t('Your Results', 'نتائجك', lang)} "
            f"<span style='font-size:0.9rem;color:#64748b;'>({len(results)} {t('tests', 'اختبارات', lang)})</span>",
            unsafe_allow_html=True,
        )

        # Colour legend
        leg_col1, leg_col2, leg_col3, leg_col4 = st.columns(4)
        leg_col1.markdown('<span style="background:#22c55e22;color:#166534;padding:3px 10px;border-radius:12px;font-size:0.8rem;">✅ Normal</span>', unsafe_allow_html=True)
        leg_col2.markdown('<span style="background:#ef444422;color:#991b1b;padding:3px 10px;border-radius:12px;font-size:0.8rem;">🔴 High</span>', unsafe_allow_html=True)
        leg_col3.markdown('<span style="background:#3b82f622;color:#1e3a8a;padding:3px 10px;border-radius:12px;font-size:0.8rem;">🔵 Low</span>', unsafe_allow_html=True)
        leg_col4.markdown('<span style="background:#94a3b822;color:#475569;padding:3px 10px;border-radius:12px;font-size:0.8rem;">⚪ Unknown</span>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for r in results:
            status   = r.get("status", "unknown").lower()
            color    = get_status_color(status)
            emoji    = get_status_emoji(status)
            value    = r.get("value", "—")
            unit     = r.get("unit", "")
            n_range  = r.get("normal_range", "—")
            test     = r.get("test_name", "—")
            explain  = r.get("explanation", "")

            # Highlight row background for abnormal results
            bg_color = f"{color}12"  # very light tint

            with st.container():
                st.markdown(
                    f"""<div style="background:{bg_color};border-left:4px solid {color};
                                 border-radius:8px;padding:14px 18px;margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                            <div>
                                <span style="font-weight:700;font-size:1rem;color:#0a2540;">{test}</span>
                                &nbsp;
                                <span style="font-size:1.1rem;font-weight:700;color:{color};">
                                    {value} {unit}
                                </span>
                            </div>
                            <div style="display:flex;gap:16px;font-size:0.85rem;color:#475569;">
                                <span>📏 {t("Normal", "المعدل الطبيعي", lang)}: <b>{n_range} {unit}</b></span>
                                <span style="background:{color}22;color:{color};padding:2px 10px;
                                             border-radius:12px;font-weight:600;">{emoji} {status.capitalize()}</span>
                            </div>
                        </div>
                        {f'<div style="margin-top:8px;font-size:0.88rem;color:#475569;line-height:1.5;">{explain}</div>' if explain else ''}
                    </div>""",
                    unsafe_allow_html=True,
                )

        # ── Quick stats ────────────────────────────────────────────────────────
        st.divider()
        normal_count  = sum(1 for r in results if r.get("status", "").lower() == "normal")
        high_count    = sum(1 for r in results if r.get("status", "").lower() == "high")
        low_count     = sum(1 for r in results if r.get("status", "").lower() == "low")
        unknown_count = sum(1 for r in results if r.get("status", "").lower() == "unknown")

        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("✅ " + t("Normal",  "طبيعي",  lang), normal_count)
        sc2.metric("🔴 " + t("High",    "مرتفع",  lang), high_count)
        sc3.metric("🔵 " + t("Low",     "منخفض",  lang), low_count)
        sc4.metric("⚪ " + t("Unknown", "غير معروف", lang), unknown_count)

        # ── Disclaimer ─────────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""<div style="background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;
                         padding:12px 16px;font-size:0.82rem;color:#78350f;">
                ⚠️ <b>{t("Medical Disclaimer:", "إخلاء المسؤولية الطبية:", lang)}</b>
                {t(
                    "This analysis is generated by AI and is for informational purposes only. "
                    "It does not constitute medical advice. Always consult a qualified healthcare "
                    "professional to interpret your lab results and make clinical decisions.",
                    "هذا التحليل مولّد بالذكاء الاصطناعي وهو لأغراض إعلامية فقط. "
                    "لا يُعدّ نصيحة طبية. استشر دائماً متخصصاً في الرعاية الصحية المؤهلاً "
                    "لتفسير نتائجك المختبرية واتخاذ القرارات السريرية.",
                    lang,
                )}
            </div>""",
            unsafe_allow_html=True,
        )

else:
    # ── Upload placeholder ─────────────────────────────────────────────────────
    st.markdown(
        f"""<div style="background:white;border:2px dashed #cbd5e1;border-radius:14px;
                     padding:48px;text-align:center;color:#94a3b8;">
            <div style="font-size:3rem;">🩸</div>
            <div style="font-size:1.1rem;font-weight:600;color:#475569;margin-top:12px;">
                {t("Upload a PDF lab report to get started", "ارفع ملف PDF لتقرير المختبر للبدء", lang)}
            </div>
            <div style="font-size:0.88rem;margin-top:8px;">
                {t("Supports blood panels, CBC, metabolic panels, lipid profiles, and more.",
                   "يدعم لوحات الدم الكاملة، CBC، الملفات الأيضية، ملف الدهون، والمزيد.", lang)}
            </div>
        </div>""",
        unsafe_allow_html=True,
    )