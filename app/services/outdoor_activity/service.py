"""
Outdoor Activity Advisor Service
Uses OpenWeatherMap API for real-time weather + air quality data.
Advises on best times to exercise outdoors, with special guidance for asthma/chest allergy patients.
"""

import streamlit as st
import requests
from app.config import OPENWEATHER_API_KEY

OPENWEATHER_BASE = "https://api.openweathermap.org"

AQI_LABELS = {
    1: {"en": "Good",      "ar": "جيد",       "color": "#22c55e", "icon": "😊"},
    2: {"en": "Fair",      "ar": "مقبول",      "color": "#84cc16", "icon": "🙂"},
    3: {"en": "Moderate",  "ar": "متوسط",      "color": "#f59e0b", "icon": "😐"},
    4: {"en": "Poor",      "ar": "رديء",       "color": "#f97316", "icon": "😷"},
    5: {"en": "Very Poor", "ar": "رديء جداً",  "color": "#ef4444", "icon": "🚫"},
}


def _get_coordinates(city: str) -> dict:
    url = f"{OPENWEATHER_BASE}/geo/1.0/direct"
    resp = requests.get(url, params={"q": city, "limit": 1, "appid": OPENWEATHER_API_KEY}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError(f"City not found: {city}")
    return {"lat": data[0]["lat"], "lon": data[0]["lon"], "name": data[0]["name"], "country": data[0].get("country", "")}


def _get_weather(lat: float, lon: float) -> dict:
    url = f"{OPENWEATHER_BASE}/data/2.5/weather"
    resp = requests.get(url, params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _get_air_quality(lat: float, lon: float) -> dict:
    url = f"{OPENWEATHER_BASE}/data/2.5/air_pollution"
    resp = requests.get(url, params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _build_advice(aqi: int, weather_raw: dict, lang: str) -> dict:
    temp = weather_raw["main"]["temp"]
    humidity = weather_raw["main"]["humidity"]
    wind_speed = weather_raw["wind"]["speed"]        # m/s
    weather_id = weather_raw["weather"][0]["id"]

    is_precipitation = weather_id < 700
    is_extreme_heat  = temp > 35
    is_extreme_cold  = temp < 5
    is_strong_wind   = wind_speed > 10              # > 36 km/h
    is_high_humidity = humidity >= 70

    safe_general = (aqi <= 2 and not is_precipitation and not is_extreme_heat
                    and not is_extreme_cold and not is_strong_wind)
    safe_asthma  = (aqi == 1 and not is_precipitation and 10 <= temp <= 30
                    and not is_high_humidity and not is_strong_wind)

    if lang == "ar":
        if aqi >= 4:
            general = "❌ يُنصح بعدم ممارسة الأنشطة الخارجية. جودة الهواء رديئة جداً وقد تسبب ضيق تنفس."
            asthma  = "🚨 تحذير: الهواء الخارجي خطير للمصابين بالربو وحساسية الصدر. ابقَ في المنزل."
        elif aqi == 3:
            general = "⚠️ الأنشطة الخفيفة مقبولة فقط. تجنب الجري المكثف وأبقِ معك البخاخ دائماً."
            asthma  = "⚠️ انتبه: جودة الهواء متوسطة. يُنصح مرضى الربو بتجنب التمارين الشديدة."
        elif aqi == 2:
            general = "🟡 جودة الهواء مقبولة. المشي خارجاً مناسب، تجنب الجري بالقرب من الطرق المزدحمة."
            asthma  = "🟡 يمكن الخروج بحذر. احمل دواءك معك واستمع لجسدك."
        else:
            general = "✅ جودة الهواء ممتازة! وقت مثالي للمشي أو الجري في الهواء الطلق."
            asthma  = "✅ آمن تماماً للمصابين بالربو. استمتع برياضتك الخارجية!"

        if is_precipitation:  general += " 🌧️ الطقس ممطر — يُنصح بتجنب الخروج."
        if is_extreme_heat:   general += " 🌡️ درجات حرارة مرتفعة جداً — تجنب أوقات الذروة."
        if is_extreme_cold:   general += " 🥶 برودة شديدة قد تُصعّب التنفس وتُثير نوبات الربو."
        if is_strong_wind:    general += " 💨 رياح قوية قد تحمل مسببات الحساسية."
        if is_high_humidity and aqi == 1:
            asthma += " 💧 ملاحظة: الرطوبة العالية قد تُسبب انزعاجاً لبعض مرضى الربو."

        best_time = "الصباح الباكر (6–8 صباحاً)" if safe_general else "يُفضَّل البقاء في الداخل"
    else:
        if aqi >= 4:
            general = "❌ Avoid outdoor activities. Air quality is very poor and may cause respiratory distress."
            asthma  = "🚨 Warning: Outdoor air is dangerous for asthma/chest allergy patients. Stay indoors."
        elif aqi == 3:
            general = "⚠️ Light activities only. Avoid intense exercise and keep your inhaler on hand."
            asthma  = "⚠️ Caution: Moderate air quality. Asthma patients should skip running or intense workouts."
        elif aqi == 2:
            general = "🟡 Fair air quality. Walking is fine; avoid jogging near busy roads."
            asthma  = "🟡 You can go out with caution. Carry your medication and listen to your body."
        else:
            general = "✅ Excellent air quality! Perfect conditions for walking or running outdoors."
            asthma  = "✅ Completely safe for asthma patients. Enjoy your outdoor workout!"

        if is_precipitation:  general += " 🌧️ Rainy conditions — avoid going out."
        if is_extreme_heat:   general += " 🌡️ Extreme heat — avoid peak afternoon hours."
        if is_extreme_cold:   general += " 🥶 Very cold air may trigger asthma attacks."
        if is_strong_wind:    general += " 💨 Strong winds may carry allergens and irritants."
        if is_high_humidity and aqi == 1:
            asthma += " 💧 Note: high humidity may still be uncomfortable for some asthma patients."

        best_time = "Early morning (6–8 AM)" if safe_general else "Stay indoors recommended"

    return {
        "safe_general": safe_general,
        "safe_asthma":  safe_asthma,
        "general":      general,
        "asthma":       asthma,
        "best_time":    best_time,
    }


@st.cache_data(ttl=600)  # cache 10 min — weather data doesn't change faster
def get_outdoor_activity_report(city: str, lang: str = "en") -> dict:
    """
    Fetch weather + AQI for a city and return outdoor activity recommendations.

    Returns:
        dict with keys: success, city_name, country, weather, aqi, components, advice, error
    """
    if not OPENWEATHER_API_KEY:
        msg = "OpenWeatherMap API key not configured. Add OPENWEATHER_API_KEY to your .env file."
        return {"success": False, "error": msg if lang == "en" else "مفتاح API للطقس غير مُعدّ في ملف .env"}

    try:
        geo     = _get_coordinates(city)
        weather = _get_weather(geo["lat"], geo["lon"])
        aq      = _get_air_quality(geo["lat"], geo["lon"])

        aqi_index  = aq["list"][0]["main"]["aqi"]
        components = aq["list"][0]["components"]
        aqi_info   = AQI_LABELS.get(aqi_index, AQI_LABELS[3])  # fallback to Moderate

        weather_info = {
            "temp":       round(weather["main"]["temp"], 1),
            "feels_like": round(weather["main"]["feels_like"], 1),
            "humidity":   weather["main"]["humidity"],
            "wind_kmh":   round(weather["wind"]["speed"] * 3.6, 1),
            "condition":  weather["weather"][0]["description"].title(),
            "icon_code":  weather["weather"][0]["icon"],
        }

        return {
            "success":   True,
            "city_name": geo["name"],
            "country":   geo["country"],
            "weather":   weather_info,
            "aqi": {
                "index":    aqi_index,
                "label_en": aqi_info["en"],
                "label_ar": aqi_info["ar"],
                "color":    aqi_info["color"],
                "icon":     aqi_info["icon"],
            },
            "components": {
                "pm2_5": round(components.get("pm2_5", 0), 1),
                "pm10":  round(components.get("pm10", 0), 1),
                "no2":   round(components.get("no2", 0), 1),
                "o3":    round(components.get("o3", 0), 1),
                "co":    round(components.get("co", 0), 1),
            },
            "advice": _build_advice(aqi_index, weather, lang),
        }

    except ValueError as e:
        msg = str(e)
        return {"success": False, "error": msg if lang == "en" else f"المدينة غير موجودة: {city}"}
    except requests.RequestException as e:
        return {"success": False, "error": f"Weather service error: {e}" if lang == "en" else f"خطأ في خدمة الطقس: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}" if lang == "en" else f"خطأ غير متوقع: {e}"}
