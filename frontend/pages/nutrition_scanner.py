import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(override=True)

"""
Nutrition Label Scanner — Streamlit Page
Scan a photo of a nutrition label → Claude Vision extracts data → chat with AI about it.
"""

import streamlit as st
from datetime import date

from frontend.utils import apply_global_styles, render_sidebar, t
from app.mcp_tools.disclaimer_injector import inject_disclaimer
from app.services.nutrition_scanner.service import (
    extract_nutrition,
    chat_about_nutrition,
    save_nutrition_entry,
    get_daily_log,
    compute_daily_totals,
)

st.set_page_config(
    page_title="Nutrition Label Scanner | MediAssist",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_global_styles()
lang = render_sidebar(active="nutrition_scanner")

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .nutrition-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0f4f8 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    }
    .nutrition-card h3 {
        color: var(--text);
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
    }
    .macro-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 12px;
        margin-top: 0.75rem;
    }
    .macro-box {
        background: #ffffff;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .macro-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text);
        line-height: 1.2;
    }
    .macro-label {
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .cal-highlight {
        background: linear-gradient(135deg, #3dbf94 0%, #2a8fa8 100%);
        color: #fff !important;
    }
    .cal-highlight .macro-value, .cal-highlight .macro-label {
        color: #fff !important;
    }
    .scan-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .scan-header h1 {
        font-size: 2rem;
        color: var(--text);
    }
    .scan-header p {
        color: var(--text-muted);
        font-size: 1rem;
    }
    .daily-total-bar {
        background: linear-gradient(135deg, var(--text) 0%, #1a3a5c 100%);
        border-radius: 16px;
        padding: 1.25rem;
        color: white;
    }
    .daily-total-bar h3 {
        color: #2a8fa8;
        margin: 0 0 0.75rem 0;
    }
    .log-item {
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.6rem;
        border-left: 4px solid #3dbf94;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .log-item-name {
        font-weight: 600;
        color: var(--text);
    }
    .log-item-cal {
        font-weight: 700;
        color: #3dbf94;
        font-size: 1.1rem;
    }
    .chat-bubble-user {
        background: var(--text);
        color: white;
        border-radius: 16px 16px 4px 16px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
        font-size: 0.95rem;
    }
    .chat-bubble-ai {
        background: #f0f4f8;
        color: var(--text);
        border-radius: 16px 16px 16px 4px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        max-width: 85%;
        font-size: 0.95rem;
        border-left: 3px solid #3dbf94;
    }
    .rtl {
        direction: rtl;
        text-align: right;
    }
    .rtl .chat-bubble-user {
        margin-left: 0;
        margin-right: auto;
        border-radius: 16px 16px 16px 4px;
    }
    .rtl .chat-bubble-ai {
        border-left: none;
        border-right: 3px solid #3dbf94;
        border-radius: 16px 16px 4px 16px;
    }
</style>
""", unsafe_allow_html=True)

# ── Label map ──────────────────────────────────────────────────────────────
LABEL_MAP = {
    "product_name":           ("Product Name",        "اسم المنتج"),
    "serving_size":           ("Serving Size",        "حجم الحصة"),
    "servings_per_container": ("Servings / Container","عدد الحصص"),
    "calories":               ("Calories",            "السعرات الحرارية"),
    "total_fat_g":            ("Total Fat (g)",       "الدهون الكلية (غ)"),
    "saturated_fat_g":        ("Saturated Fat (g)",   "الدهون المشبعة (غ)"),
    "trans_fat_g":            ("Trans Fat (g)",       "الدهون المتحولة (غ)"),
    "cholesterol_mg":         ("Cholesterol (mg)",    "الكوليسترول (ملغ)"),
    "sodium_mg":              ("Sodium (mg)",         "الصوديوم (ملغ)"),
    "total_carbohydrates_g":  ("Total Carbs (g)",     "الكربوهيدرات (غ)"),
    "dietary_fiber_g":        ("Fiber (g)",           "الألياف (غ)"),
    "total_sugars_g":         ("Total Sugars (g)",    "السكريات (غ)"),
    "added_sugars_g":         ("Added Sugars (g)",    "السكريات المضافة (غ)"),
    "protein_g":              ("Protein (g)",         "البروتين (غ)"),
    "vitamin_d_mcg":          ("Vitamin D (mcg)",     "فيتامين د (مكغ)"),
    "calcium_mg":             ("Calcium (mg)",        "الكالسيوم (ملغ)"),
    "iron_mg":                ("Iron (mg)",           "الحديد (ملغ)"),
    "potassium_mg":           ("Potassium (mg)",      "البوتاسيوم (ملغ)"),
}

MACRO_KEYS = ["calories", "protein_g", "total_carbohydrates_g", "total_fat_g", "dietary_fiber_g", "sodium_mg"]


def _lbl(key: str) -> str:
    en, ar = LABEL_MAP.get(key, (key, key))
    return ar if lang == "ar" else en


def _fmt(val) -> str:
    if val is None:
        return "—"
    if isinstance(val, float):
        return f"{val:g}"
    return str(val)


def render_macro_grid(data: dict, highlight_calories: bool = True):
    cols = st.columns(len(MACRO_KEYS))
    for i, key in enumerate(MACRO_KEYS):
        val = data.get(key)
        css_class = "macro-box cal-highlight" if key == "calories" and highlight_calories else "macro-box"
        with cols[i]:
            st.markdown(f"""
            <div class="{css_class}">
                <div class="macro-value">{_fmt(val)}</div>
                <div class="macro-label">{_lbl(key)}</div>
            </div>
            """, unsafe_allow_html=True)


DV_REFERENCE = {
    "total_fat_g": 78, "saturated_fat_g": 20, "cholesterol_mg": 300,
    "sodium_mg": 2300, "total_carbohydrates_g": 275, "dietary_fiber_g": 28,
    "added_sugars_g": 50, "protein_g": 50, "vitamin_d_mcg": 20,
    "calcium_mg": 1300, "iron_mg": 18, "potassium_mg": 4700,
}

def _dv_badge(key: str, val) -> str:
    if val is None or key not in DV_REFERENCE:
        return ""
    try:
        pct = round(float(val) / DV_REFERENCE[key] * 100)
    except (TypeError, ZeroDivisionError):
        return ""
    if pct <= 10:
        bg, fg = "#e8f5f0", "#2a9e78"
    elif pct <= 19:
        bg, fg = "#fef3c7", "#854f0b"
    else:
        bg, fg = "#fdeaea", "#a32d2d"
    return f"<span style='background:{bg};color:{fg};font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px;'>{pct}% DV</span>"


def render_full_table(data: dict):
    skip = {"product_name", "serving_size", "servings_per_container"}
    rows_html = ""
    for key, (en, ar) in LABEL_MAP.items():
        if key in skip:
            continue
        label = ar if lang == "ar" else en
        raw = data.get(key)
        val = _fmt(raw)
        badge = _dv_badge(key, raw)
        rows_html += (
            f"<tr style='border-bottom:1px solid var(--border);'>"
            f"<td style='padding:8px 12px;color:var(--text-mid);font-weight:500;'>{label}</td>"
            f"<td style='padding:8px 12px;font-weight:600;color:var(--text);'>{val}</td>"
            f"<td style='padding:8px 12px;text-align:right;'>{badge}</td>"
            f"</tr>"
        )

    st.markdown(f"""
    <div class="nutrition-card">
        <h3>{t("Full Nutrition Facts", "جدول القيم الغذائية الكامل", lang)}</h3>
        <table style="width:100%;border-collapse:collapse;">
            {rows_html}
        </table>
        <div style="font-size:11px;color:var(--text-muted);margin-top:8px;">
            * {t("% Daily Value based on a 2,000 calorie diet","% القيمة اليومية مبنية على نظام غذائي 2000 سعرة",lang)}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Page header ────────────────────────────────────────────────────────────
dir_class = "rtl" if lang == "ar" else ""
st.markdown(f"""
<div class="scan-header {dir_class}">
    <h1>📸 {t("Nutrition Label Scanner", "ماسح ملصق القيم الغذائية", lang)}</h1>
    <p>{t(
        "Scan a nutrition label photo — AI extracts the data, then you can ask questions about it",
        "صوّر ملصق القيم الغذائية — يستخرج الذكاء الاصطناعي البيانات ثم يمكنك طرح الأسئلة عليه",
        lang
    )}</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────
tab_scan, tab_log = st.tabs([
    t("🔍 Scan Label", "🔍 مسح الملصق", lang),
    t("📋 Daily Log", "📋 السجل اليومي", lang),
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — SCAN + CHAT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_scan:

    col_input, col_result = st.columns([1, 1], gap="large")

    # ── LEFT: Upload / Camera ──────────────────────────────────────
    with col_input:
        st.subheader(t("📷 Capture or Upload", "📷 التقط أو ارفع صورة", lang))

        input_method = st.radio(
            t("Choose input method", "اختر طريقة الإدخال", lang),
            [t("📷 Camera", "📷 الكاميرا", lang), t("📁 Upload Image", "📁 رفع صورة", lang)],
            horizontal=True,
            label_visibility="collapsed",
        )

        image_bytes = None
        mime_type = "image/jpeg"

        if input_method == t("📷 Camera", "📷 الكاميرا", lang):
            camera_photo = st.camera_input(
                t("Point at the nutrition label", "وجّه الكاميرا نحو ملصق القيم الغذائية", lang)
            )
            if camera_photo:
                image_bytes = camera_photo.getvalue()
                mime_type = "image/jpeg"
        else:
            uploaded = st.file_uploader(
                t("Upload a photo of the nutrition label", "ارفع صورة ملصق القيم الغذائية", lang),
                type=["jpg", "jpeg", "png", "webp"],
            )
            if uploaded:
                image_bytes = uploaded.getvalue()
                ext = uploaded.name.rsplit(".", 1)[-1].lower()
                mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
                mime_type = mime_map.get(ext, "image/jpeg")

        if image_bytes:
            st.image(image_bytes, caption=t("Captured image", "الصورة الملتقطة", lang), use_container_width=True)

        if image_bytes:
            if st.button(
                t("🔍 Extract Nutrition", "🔍 استخراج القيم الغذائية", lang),
                type="primary",
                use_container_width=True,
            ):
                with st.spinner(t("Analyzing label with AI...", "جاري تحليل الملصق بالذكاء الاصطناعي...", lang)):
                    result = extract_nutrition(image_bytes, mime_type, lang)

                if "error" in result:
                    st.error(result["error"])
                else:
                    st.session_state["scanned_nutrition"] = result
                    st.session_state["label_chat_history"] = []
                    st.success(t("✅ Nutrition data extracted!", "✅ تم استخراج القيم الغذائية!", lang))

    # ── RIGHT: Results + Chat ──────────────────────────────────────
    with col_result:
        if "scanned_nutrition" in st.session_state:
            data = st.session_state["scanned_nutrition"]

            # Product name / serving
            pname = data.get("product_name")
            if pname:
                st.subheader(pname)
            serving = data.get("serving_size")
            if serving:
                st.caption(f"{_lbl('serving_size')}: {serving}")

            # Macro grid
            render_macro_grid(data)

            # Full nutrition table
            render_full_table(data)

            # Save to daily log
            st.markdown("---")
            notes = st.text_input(
                t("Add a note (optional)", "أضف ملاحظة (اختياري)", lang),
                placeholder=t("e.g. Breakfast cereal", "مثال: حبوب الإفطار", lang),
                key="notes_input",
            )
            if st.button(
                t("💾 Save to Daily Log", "💾 حفظ في السجل اليومي", lang),
                type="secondary",
                use_container_width=True,
            ):
                with st.spinner(t("Saving...", "جاري الحفظ...", lang)):
                    res = save_nutrition_entry(data, lang, notes)
                if res.get("success"):
                    st.success(t("Saved to your daily log!", "تم الحفظ في سجلك اليومي!", lang))
                    disclaimer = inject_disclaimer("", lang)
                    if disclaimer:
                        st.info(disclaimer)
                else:
                    st.error(res.get("error", t("Failed to save.", "فشل الحفظ.", lang)))

            # ── CHAT SECTION ──────────────────────────────────────
            st.markdown("---")
            st.markdown(f"### 💬 {t('Ask AI about this label', 'اسأل الذكاء الاصطناعي عن هذا الملصق', lang)}")
            st.caption(t(
                "Ask anything about the nutrition data — is it healthy? how much protein? safe for diabetics?",
                "اسأل أي شيء عن القيم الغذائية — هل هو صحي؟ كم البروتين؟ آمن لمرضى السكري؟",
                lang,
            ))

            # Initialize chat history if not present
            if "label_chat_history" not in st.session_state:
                st.session_state["label_chat_history"] = []

            # Display existing chat messages
            chat_history = st.session_state["label_chat_history"]
            if chat_history:
                dir_attr = 'class="rtl"' if lang == "ar" else ""
                chat_html = f"<div {dir_attr}>"
                for msg in chat_history:
                    if msg["role"] == "user":
                        chat_html += f'<div class="chat-bubble-user">🧑 {msg["content"]}</div>'
                    else:
                        chat_html += f'<div class="chat-bubble-ai">🤖 {msg["content"]}</div>'
                chat_html += "</div>"
                st.markdown(chat_html, unsafe_allow_html=True)

            # Chat input
            with st.form(key="chat_form", clear_on_submit=True):
                chat_col1, chat_col2 = st.columns([5, 1])
                with chat_col1:
                    user_question = st.text_input(
                        t("Your question", "سؤالك", lang),
                        placeholder=t(
                            "e.g. Is this high in sodium?",
                            "مثال: هل يحتوي على نسبة عالية من الصوديوم؟",
                            lang,
                        ),
                        label_visibility="collapsed",
                    )
                with chat_col2:
                    send = st.form_submit_button(
                        t("Send", "إرسال", lang),
                        use_container_width=True,
                        type="primary",
                    )

            if send and user_question.strip():
                with st.spinner(t("Thinking...", "جاري التفكير...", lang)):
                    answer = chat_about_nutrition(
                        question=user_question,
                        nutrition_context=data,
                        history=chat_history,
                        language=lang,
                    )

                st.session_state["label_chat_history"].append({"role": "user", "content": user_question})
                st.session_state["label_chat_history"].append({"role": "assistant", "content": answer})
                st.rerun()

            # Clear chat button
            if chat_history:
                if st.button(t("🗑️ Clear chat", "🗑️ مسح المحادثة", lang), use_container_width=True):
                    st.session_state["label_chat_history"] = []
                    st.rerun()

        else:
            st.markdown(f"""
            <div class="nutrition-card" style="text-align:center;padding:3rem;">
                <p style="font-size:3rem;margin-bottom:0.5rem;">📸</p>
                <p style="color:var(--text-muted);">{t(
                    "Capture or upload a nutrition label to see results and chat with AI",
                    "التقط أو ارفع صورة لملصق القيم الغذائية لرؤية النتائج والتحدث مع الذكاء الاصطناعي",
                    lang
                )}</p>
            </div>
            """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — DAILY LOG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_log:
    st.subheader(t("📋 Daily Nutrition Log", "📋 سجل التغذية اليومي", lang))

    selected_date = st.date_input(
        t("Select date", "اختر التاريخ", lang),
        value=date.today(),
        max_value=date.today(),
    )

    entries = get_daily_log(selected_date)

    if not entries:
        st.info(t(
            "No entries for this date. Scan a label to get started!",
            "لا توجد إدخالات لهذا التاريخ. امسح ملصقاً للبدء!",
            lang,
        ))
    else:
        totals = compute_daily_totals(entries)
        st.markdown(f"""
        <div class="daily-total-bar">
            <h3>{t("Daily Totals", "الإجمالي اليومي", lang)}</h3>
        </div>
        """, unsafe_allow_html=True)

        render_macro_grid(totals, highlight_calories=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"**{t('Scanned Items', 'العناصر الممسوحة', lang)}** ({len(entries)})")
        for entry in entries:
            name = entry.get("product_name") or entry.get("notes") or t("Unnamed item", "عنصر بدون اسم", lang)
            cal = entry.get("calories")
            cal_display = f"{cal} kcal" if cal else "—"
            time_str = ""
            if entry.get("scanned_at"):
                try:
                    dt = entry["scanned_at"]
                    if isinstance(dt, str):
                        from datetime import datetime as _dt
                        dt = _dt.fromisoformat(dt.replace("Z", "+00:00"))
                    time_str = dt.strftime("%I:%M %p")
                except Exception:
                    time_str = ""

            st.markdown(f"""
            <div class="log-item">
                <div>
                    <span class="log-item-name">{name}</span>
                    <span style="color:#94a3b8;font-size:0.85rem;margin-left:10px;">{time_str}</span>
                </div>
                <span class="log-item-cal">{cal_display}</span>
            </div>
            """, unsafe_allow_html=True)

        disclaimer = inject_disclaimer("", lang)
        if disclaimer:
            st.caption(disclaimer)