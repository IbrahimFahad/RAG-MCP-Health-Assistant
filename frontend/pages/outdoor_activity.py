import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from frontend.utils import apply_global_styles, render_sidebar, t
from app.services.outdoor_activity.service import get_outdoor_activity_report

st.set_page_config(
    page_title="Outdoor Activity Advisor | MediAssist",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_global_styles()
lang = render_sidebar(active="outdoor_activity")

rtl = ' class="rtl"' if lang == "ar" else ""

# ── Extra CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.weather-card {
    background: var(--card);
    border-radius: 16px;
    border: 1px solid var(--border);
    padding: 20px;
    text-align: center;
}
.aqi-badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 1rem;
    color: #fff;
    margin-top: 6px;
}
.advice-card {
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 10px;
    font-size: 14px;
    line-height: 1.7;
}
.comp-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
}
.comp-val { font-weight: 600; color: var(--text); }
.comp-lbl { color: var(--text-muted); }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div{rtl} style="margin-bottom:20px;">
  <div class="page-title">🌤️ {t("Outdoor Activity Advisor", "مستشار النشاط الخارجي", lang)}</div>
  <div class="page-subtitle">
    {t(
        "Check real-time air quality & weather before running or walking outdoors — essential for asthma & chest allergy patients.",
        "تحقق من جودة الهواء والطقس الفعلي قبل الركض أو المشي — ضروري لمرضى الربو وحساسية الصدر.",
        lang
    )}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Input ────────────────────────────────────────────────────────────────────
col_in, col_btn = st.columns([4, 1])
with col_in:
    city_input = st.text_input(
        t("Enter city name", "أدخل اسم المدينة", lang),
        placeholder=t("e.g. Riyadh, London, Cairo", "مثال: الرياض، لندن، القاهرة", lang),
        label_visibility="collapsed",
    )
with col_btn:
    check_clicked = st.button(t("🔍 Check", "🔍 فحص", lang), use_container_width=True, type="primary")

# ── Quick city chips ─────────────────────────────────────────────────────────
# Tuples of (display_label, api_name) — always send English to the API
quick_cities = (
    [("Riyadh", "Riyadh"), ("Dubai", "Dubai"), ("Cairo", "Cairo"),
     ("London", "London"), ("Jeddah", "Jeddah")]
    if lang == "en" else
    [("الرياض", "Riyadh"), ("دبي", "Dubai"), ("القاهرة", "Cairo"),
     ("لندن", "London"),  ("جدة", "Jeddah")]
)
st.markdown(f"<small style='color:#9ca3af'>{t('Quick cities:', 'مدن سريعة:', lang)}</small>", unsafe_allow_html=True)
city_cols = st.columns(len(quick_cities))
for i, (label, api_name) in enumerate(quick_cities):
    with city_cols[i]:
        if st.button(f"🏙️ {label}", key=f"qc_{i}", use_container_width=True):
            st.session_state["city_override"] = api_name
            st.rerun()

if "city_override" in st.session_state:
    city_input = st.session_state.pop("city_override")
    check_clicked = True

# ── Results ──────────────────────────────────────────────────────────────────
if check_clicked and city_input:
    with st.spinner(t("Fetching weather & air quality data…", "جارٍ جلب بيانات الطقس وجودة الهواء…", lang)):
        report = get_outdoor_activity_report(city_input.strip(), lang)

    if not report["success"]:
        st.error(report["error"])
    else:
        w    = report["weather"]
        aqi  = report["aqi"]
        comp = report["components"]
        adv  = report["advice"]

        city_label = f"{report['city_name']}, {report['country']}"
        aqi_label  = t(aqi["label_en"], aqi["label_ar"], lang)

        # ── Row 1: Weather + AQI ─────────────────────────────────────────
        wc, ac = st.columns(2, gap="small")

        with wc:
            icon_url = f"https://openweathermap.org/img/wn/{w['icon_code']}@2x.png"
            st.markdown(f"""
            <div class="weather-card">
                <div style="font-size:12px;color:var(--text-muted);margin-bottom:4px;">
                    📍 {city_label}
                </div>
                <img src="{icon_url}" style="width:64px;height:64px;" />
                <div style="font-size:2.2rem;font-weight:700;color:var(--text);">{w['temp']}°C</div>
                <div style="font-size:13px;color:var(--text-mid);margin:4px 0;">{w['condition']}</div>
                <div style="display:flex;justify-content:center;gap:20px;margin-top:10px;font-size:12px;color:var(--text-muted);">
                    <span>💧 {w['humidity']}%</span>
                    <span>🌡️ {t("Feels","يُحسّ",lang)} {w['feels_like']}°C</span>
                    <span>💨 {w['wind_kmh']} km/h</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with ac:
            st.markdown(f"""
            <div class="weather-card" style="height:100%;">
                <div style="font-size:12px;color:var(--text-muted);margin-bottom:6px;">
                    {t("Air Quality Index", "مؤشر جودة الهواء", lang)}
                </div>
                <div style="font-size:4rem;">{aqi["icon"]}</div>
                <div class="aqi-badge" style="background:{aqi['color']};">{aqi_label}</div>
                <div style="font-size:12px;color:var(--text-muted);margin-top:8px;">
                    AQI {aqi['index']} / 5
                </div>
                <div style="margin-top:12px;">
                    <div class="comp-row">
                        <span class="comp-lbl">PM2.5</span>
                        <span class="comp-val">{comp['pm2_5']} µg/m³</span>
                    </div>
                    <div class="comp-row">
                        <span class="comp-lbl">PM10</span>
                        <span class="comp-val">{comp['pm10']} µg/m³</span>
                    </div>
                    <div class="comp-row">
                        <span class="comp-lbl">NO₂</span>
                        <span class="comp-val">{comp['no2']} µg/m³</span>
                    </div>
                    <div class="comp-row" style="border-bottom:none;">
                        <span class="comp-lbl">O₃</span>
                        <span class="comp-val">{comp['o3']} µg/m³</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        # ── Row 2: Recommendations ───────────────────────────────────────
        gc, as_c = st.columns(2, gap="small")

        with gc:
            bg_color = "#e8f5f0" if adv["safe_general"] else "#fef2f2"
            st.markdown(f"""
            <div class="advice-card" style="background:{bg_color};border:1px solid var(--border);">
                <div style="font-size:13px;font-weight:600;color:var(--text);margin-bottom:8px;">
                    🏃 {t("General Activity Advice", "نصيحة النشاط العام", lang)}
                </div>
                <div style="color:var(--text);">{adv['general']}</div>
                <div style="margin-top:10px;font-size:12px;color:var(--text-muted);">
                    🕐 {t("Best time:", "أفضل وقت:", lang)} <strong>{adv['best_time']}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with as_c:
            as_bg = "#e8f5f0" if adv["safe_asthma"] else "#fef2f2"
            st.markdown(f"""
            <div class="advice-card" style="background:{as_bg};border:1px solid var(--border);">
                <div style="font-size:13px;font-weight:600;color:var(--text);margin-bottom:8px;">
                    🫁 {t("Asthma & Chest Allergy Patients", "مرضى الربو وحساسية الصدر", lang)}
                </div>
                <div style="color:var(--text);">{adv['asthma']}</div>
                <div style="margin-top:10px;font-size:12px;color:var(--text-muted);">
                    {t(
                        "Always carry your rescue inhaler outdoors.",
                        "احمل دائماً بخاخ الإسعاف عند الخروج.",
                        lang
                    )}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Disclaimer ───────────────────────────────────────────────────
        st.markdown(f"""
        <div class="disclaimer">
            ⚠️ {t(
                "This advisory is based on real-time data but does not replace medical advice. "
                "Consult your doctor before starting any outdoor exercise program.",
                "هذه النصائح مبنية على بيانات لحظية ولا تُغني عن الاستشارة الطبية. "
                "استشر طبيبك قبل البدء بأي برنامج رياضة خارجية.",
                lang
            )}
        </div>
        """, unsafe_allow_html=True)

elif check_clicked and not city_input:
    st.warning(t("Please enter a city name.", "يرجى إدخال اسم المدينة.", lang))
