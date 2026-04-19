import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from frontend.utils import apply_global_styles, render_sidebar, t
from app.services.restaurant_nutrition.service import (
    get_all_restaurants,
    get_restaurant_menu,
    search_items,
    get_lowest_calorie_items,
    ask_restaurant_ai,
)

st.set_page_config(
    page_title="Restaurant Nutrition | MediAssist",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_global_styles()
lang = render_sidebar(active="restaurant_nutrition")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.rest-chip {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    border: 1.5px solid var(--border);
    background: var(--card);
    color: var(--text);
    margin: 3px;
    transition: all 0.15s;
}
.rest-chip.active {
    background: #3dbf94;
    color: #1a2e2a;
    border-color: #3dbf94;
}
.item-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 8px;
}
.item-card:hover {
    border-color: rgba(61,191,148,0.4);
}
.cal-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 700;
}
.macro-mini {
    display: inline-block;
    font-size: 11px;
    color: var(--text-muted);
    margin-right: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
rtl = ' class="rtl"' if lang == "ar" else ""
st.markdown(f"""
<div{rtl}>
  <div class="page-title">🍽️ {t("Restaurant Nutrition Guide", "دليل التغذية في المطاعم", lang)}</div>
  <div class="page-subtitle">{t(
    "Explore calories & nutrition for popular Saudi restaurant menus — then ask AI anything.",
    "استكشف السعرات والقيم الغذائية لقوائم المطاعم السعودية الشهيرة — ثم اسأل الذكاء الاصطناعي.",
    lang)}</div>
</div>
""", unsafe_allow_html=True)

# ── State ─────────────────────────────────────────────────────────────────────
if "rest_key" not in st.session_state:
    st.session_state.rest_key = None
if "rest_tab" not in st.session_state:
    st.session_state.rest_tab = "browse"
if "rest_chat" not in st.session_state:
    st.session_state.rest_chat = []

all_restaurants = get_all_restaurants()

# ── Restaurant selector ───────────────────────────────────────────────────────
st.markdown(f"<div style='font-size:12px;color:var(--text-muted);margin-bottom:6px;'>{t('Select a restaurant (or browse all):','اختر مطعمًا (أو تصفح الكل):',lang)}</div>", unsafe_allow_html=True)

cols = st.columns(len(all_restaurants) + 1)
with cols[0]:
    if st.button(f"🌍 {t('All','الكل',lang)}", key="btn_all", use_container_width=True):
        st.session_state.rest_key = None
        st.session_state.rest_chat = []
        st.rerun()

for i, rest in enumerate(all_restaurants):
    with cols[i + 1]:
        label = rest["name_ar"] if lang == "ar" else rest["name_en"]
        is_active = st.session_state.rest_key == rest["key"]
        btn_type = "primary" if is_active else "secondary"
        if st.button(f"{rest['emoji']} {label}", key=f"rb_{rest['key']}", use_container_width=True, type=btn_type):
            if st.session_state.rest_key == rest["key"]:
                st.session_state.rest_key = None
            else:
                st.session_state.rest_key = rest["key"]
                st.session_state.rest_chat = []
            st.rerun()

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Active restaurant banner ──────────────────────────────────────────────────
selected_key = st.session_state.rest_key
selected_rest = get_restaurant_menu(selected_key) if selected_key else None

if selected_rest:
    rname = selected_rest["name_ar"] if lang == "ar" else selected_rest["name_en"]
    st.markdown(f"""
<div style="background:{selected_rest['color']}18;border:1px solid {selected_rest['color']}40;
            border-radius:14px;padding:16px 20px;margin-bottom:16px;
            display:flex;align-items:center;gap:16px;">
    <span style="font-size:2.5rem;">{selected_rest['emoji']}</span>
    <div>
        <div style="font-size:1.1rem;font-weight:700;color:var(--text);">{rname}</div>
        <div style="font-size:0.85rem;color:var(--text-muted);">
            {selected_rest['category']} · {len(selected_rest['items'])} {t('menu items','عناصر في القائمة',lang)}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_browse, tab_search, tab_best, tab_chat = st.tabs([
    t("📋 Browse Menu", "📋 تصفح القائمة", lang),
    t("🔍 Search", "🔍 بحث", lang),
    t("💚 Healthiest Picks", "💚 أفضل الخيارات", lang),
    t("🤖 Ask AI", "🤖 اسأل الذكاء الاصطناعي", lang),
])

# ── helper: render item card ──────────────────────────────────────────────────
def cal_color(cal: int) -> str:
    if cal < 300: return ("#e8f5f0", "#2a9e78")
    if cal < 600: return ("#fef3c7", "#854f0b")
    return ("#fdeaea", "#a32d2d")

def item_card_html(item: dict, show_rest: bool = False) -> str:
    bg, fg = cal_color(item["calories"])
    name = item["name_ar"] if lang == "ar" else item["name_en"]
    rest_tag = f"<span style='font-size:11px;color:var(--text-muted);margin-left:8px;'>{item.get('restaurant_emoji','')} {item.get('restaurant_en','')}</span>" if show_rest else ""
    return f"""
<div class="item-card">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
    <div>
      <span style="font-weight:600;color:var(--text);">{name}</span>{rest_tag}
      <div style="margin-top:4px;">
        <span class="macro-mini">🥩 {item['protein_g']}g protein</span>
        <span class="macro-mini">🍞 {item['carbs_g']}g carbs</span>
        <span class="macro-mini">🫙 {item['fat_g']}g fat</span>
        <span class="macro-mini">🧂 {item['sodium_mg']}mg sodium</span>
      </div>
    </div>
    <span class="cal-pill" style="background:{bg};color:{fg};">{item['calories']} kcal</span>
  </div>
</div>"""

# ── TAB 1: Browse Menu ────────────────────────────────────────────────────────
with tab_browse:
    scope_restaurants = [selected_rest] if selected_rest else [r for r in RESTAURANTS.values()]

    # Import RESTAURANTS for direct access
    from app.services.restaurant_nutrition.data import RESTAURANTS as _DATA

    if selected_rest:
        scope = {selected_key: selected_rest}
    else:
        scope = _DATA

    for key, rest in scope.items():
        rname = rest["name_ar"] if lang == "ar" else rest["name_en"]
        with st.expander(f"{rest['emoji']} {rname}  ({len(rest['items'])} items)", expanded=(selected_key == key)):
            categories = sorted(set(i["category"] for i in rest["items"]))
            for cat in categories:
                items_in_cat = [i for i in rest["items"] if i["category"] == cat]
                st.markdown(f"<div style='font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;margin:8px 0 4px;'>{cat}</div>", unsafe_allow_html=True)
                for item in sorted(items_in_cat, key=lambda x: x["calories"]):
                    st.markdown(item_card_html(item), unsafe_allow_html=True)

# ── TAB 2: Search ─────────────────────────────────────────────────────────────
with tab_search:
    s_col, _ = st.columns([3, 1])
    query = s_col.text_input(
        t("Search for a dish...", "ابحث عن طبق...", lang),
        placeholder=t("e.g. zinger, shawarma, salad, fries", "مثال: زينجر، شاورما، سلطة، بطاطس", lang),
        label_visibility="collapsed",
    )
    if query:
        results = search_items(query, selected_key)
        if results:
            st.markdown(f"<div style='font-size:12px;color:var(--text-muted);margin-bottom:8px;'>{len(results)} {t('results','نتيجة',lang)}</div>", unsafe_allow_html=True)
            for item in sorted(results, key=lambda x: x["calories"]):
                st.markdown(item_card_html(item, show_rest=not selected_key), unsafe_allow_html=True)
        else:
            st.info(t("No items found. Try a different keyword.", "لم يتم العثور على نتائج. جرّب كلمة مختلفة.", lang))
    else:
        st.markdown(f"<div style='color:var(--text-muted);font-size:0.9rem;'>{t('Type above to search across all menus.','اكتب أعلاه للبحث في جميع القوائم.',lang)}</div>", unsafe_allow_html=True)

# ── TAB 3: Healthiest Picks ───────────────────────────────────────────────────
with tab_best:
    n_items = st.slider(t("Show top N lowest-calorie items", "عرض أفضل N خيارات قليلة السعرات", lang), 5, 20, 10, key="n_slider")
    best = get_lowest_calorie_items(selected_key, top_n=n_items)
    st.markdown(f"<div style='font-size:12px;color:var(--text-muted);margin-bottom:8px;'>{t('Sorted by calories (lowest first), excluding drinks & sauces.','مرتبة حسب السعرات (الأقل أولًا)، باستثناء المشروبات والصلصات.',lang)}</div>", unsafe_allow_html=True)
    for item in best:
        st.markdown(item_card_html(item, show_rest=not selected_key), unsafe_allow_html=True)

# ── TAB 4: Ask AI ─────────────────────────────────────────────────────────────
with tab_chat:
    rest_label = (selected_rest["name_ar"] if lang == "ar" else selected_rest["name_en"]) if selected_rest else t("all restaurants", "جميع المطاعم", lang)

    # Quick prompt chips
    quick = (
        [f"What's the healthiest meal at {rest_label}?",
         f"What has the most protein at {rest_label}?",
         f"Compare burgers by calories",
         f"What can I eat under 400 calories?"]
        if lang == "en" else
        [f"ما أصح وجبة في {rest_label}؟",
         f"ما الأعلى بروتيناً في {rest_label}؟",
         f"قارن البرغر من حيث السعرات",
         f"ما الذي يمكنني تناوله تحت 400 سعرة؟"]
    )
    st.markdown(f"<div style='font-size:11px;color:var(--text-muted);margin-bottom:6px;'>{t('Quick questions:','أسئلة سريعة:',lang)}</div>", unsafe_allow_html=True)
    qcols = st.columns(len(quick))
    for i, q in enumerate(quick):
        with qcols[i]:
            if st.button(q, key=f"qq_{i}", use_container_width=True):
                st.session_state["rest_pending_q"] = q
                st.rerun()

    # Chat history
    for msg in st.session_state.rest_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if "rest_pending_q" in st.session_state:
        user_q = st.session_state.pop("rest_pending_q")
    else:
        user_q = st.chat_input(t("Ask about any meal or restaurant...", "اسأل عن أي وجبة أو مطعم...", lang))

    if user_q:
        st.session_state.rest_chat.append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.markdown(user_q)

        with st.chat_message("assistant"):
            with st.spinner(t("Looking up nutrition data...", "جارٍ البحث عن البيانات الغذائية...", lang)):
                result = ask_restaurant_ai(user_q, selected_key, language=lang)

            st.markdown(result["answer"])

            if result["items_mentioned"]:
                st.markdown(f"<div style='font-size:11px;color:var(--text-muted);margin-top:8px;'>{t('Items mentioned:','العناصر المذكورة:',lang)}</div>", unsafe_allow_html=True)
                for item in result["items_mentioned"]:
                    st.markdown(item_card_html(item, show_rest=True), unsafe_allow_html=True)

            st.session_state.rest_chat.append({"role": "assistant", "content": result["answer"]})

    if st.session_state.rest_chat:
        if st.button(t("🗑️ Clear chat", "🗑️ مسح المحادثة", lang), key="clear_rest_chat"):
            st.session_state.rest_chat = []
            st.rerun()

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;
            padding:10px 14px;font-size:0.82rem;color:#92400e;margin-top:16px;">
    ⚠️ {t(
        "Nutrition values are approximate and may vary by preparation method, location, and portion size. Always verify with the restaurant directly.",
        "القيم الغذائية تقريبية وقد تختلف حسب طريقة التحضير والموقع وحجم الحصة. تحقق دائمًا مع المطعم مباشرةً.",
        lang)}
</div>
""", unsafe_allow_html=True)