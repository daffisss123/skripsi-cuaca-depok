import json
from pathlib import Path

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="Cuaca Kota Depok",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# KONSTANTA
# =========================
LAT_DEPOK = -6.4025
LON_DEPOK = 106.7942
CACHE_FILE = Path("data/processed/live_weather_cache.json")

KECAMATAN = [
    {"nama": "Beji",         "lat": -6.3750, "lon": 106.8300},
    {"nama": "Bojongsari",   "lat": -6.4400, "lon": 106.7500},
    {"nama": "Cilodong",     "lat": -6.4100, "lon": 106.8400},
    {"nama": "Cimanggis",    "lat": -6.3700, "lon": 106.8800},
    {"nama": "Cinere",       "lat": -6.3600, "lon": 106.7800},
    {"nama": "Cipayung",     "lat": -6.4300, "lon": 106.8600},
    {"nama": "Limo",         "lat": -6.3900, "lon": 106.7700},
    {"nama": "Pancoran Mas", "lat": -6.4000, "lon": 106.8200},
    {"nama": "Sawangan",     "lat": -6.4500, "lon": 106.7700},
    {"nama": "Sukmajaya",    "lat": -6.3800, "lon": 106.8500},
    {"nama": "Tapos",        "lat": -6.3600, "lon": 106.8900},
]

# =========================
# SHARED STYLE
# =========================
STYLE = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:wght@700&display=swap" rel="stylesheet">
<style>
/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── App background — light blue-grey ── */
.stApp {
    background: linear-gradient(150deg, #eef4fb 0%, #ddeaf8 50%, #e8f1fa 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #d4e2f0 !important;
    box-shadow: 2px 0 12px rgba(30,80,160,0.06);
}
[data-testid="stSidebar"] * { color: #2c4a6e !important; }
[data-testid="stSidebar"] a:hover { color: #1a6bc4 !important; }

/* ── Streamlit header bar ── */
header[data-testid="stHeader"] {
    background: rgba(238,244,251,0.92) !important;
    backdrop-filter: blur(8px);
    border-bottom: 1px solid #c8ddf0;
}
header[data-testid="stHeader"]::before { background: transparent !important; }
header[data-testid="stHeader"] button,
header[data-testid="stHeader"] a,
header[data-testid="stHeader"] svg { color: #2c4a6e !important; fill: #2c4a6e !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── Hero / page header card ── */
.hero-banner, .page-header {
    background: linear-gradient(135deg, #1a6bc4 0%, #1252a3 100%);
    border-radius: 20px;
    padding: 2rem 2.4rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(26,107,196,0.22);
}
.hero-banner::before, .page-header::before {
    content: "";
    position: absolute; top: -80px; right: -80px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

/* Badge inside hero */
.hero-badge, .page-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.35);
    color: #e0f0ff;
    font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.09em; text-transform: uppercase;
    padding: 0.25rem 0.8rem; border-radius: 20px;
    margin-bottom: 0.8rem;
}
.hero-title, .page-title {
    font-size: 2.1rem; font-weight: 800;
    color: #ffffff; margin: 0 0 0.4rem; letter-spacing: -0.5px;
}
.hero-sub, .page-sub {
    color: rgba(255,255,255,0.82);
    font-size: 0.95rem; line-height: 1.65; max-width: 640px; margin: 0;
}

/* ── Section title ── */
.section-title {
    font-size: 1.05rem; font-weight: 700; color: #1a3a5c;
    margin: 1.8rem 0 0.85rem;
    display: flex; align-items: center; gap: 0.45rem;
}
.section-title::after {
    content: ""; flex: 1; height: 2px;
    background: linear-gradient(90deg, #b8d4f0, transparent);
    margin-left: 0.4rem; border-radius: 2px;
}

/* ── Metric cards ── */
div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #c8ddf0 !important;
    border-radius: 16px !important;
    padding: 1.1rem 1rem !important;
    box-shadow: 0 2px 12px rgba(30,80,160,0.07);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 24px rgba(26,107,196,0.14) !important;
}
div[data-testid="stMetric"] label {
    color: #5580a8 !important;
    font-size: 0.76rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.06em !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #0f2d56 !important;
    font-size: 1.7rem !important; font-weight: 700 !important;
    font-family: 'Space Mono', monospace !important;
}

/* ── Info card ── */
.info-card {
    background: #e8f3ff;
    border: 1px solid #b8d4f0;
    border-left: 4px solid #1a6bc4;
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    color: #1a3a5c;
    font-size: 0.88rem; line-height: 1.6;
    margin-bottom: 1rem;
}

/* ── Forecast cards ── */
.forecast-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 0.65rem; margin-top: 0.4rem;
}
@media (max-width: 900px) {
    .forecast-grid { grid-template-columns: repeat(4, 1fr); }
}
@media (max-width: 560px) {
    .forecast-grid { grid-template-columns: repeat(2, 1fr); }
    .hero-title, .page-title { font-size: 1.5rem; }
    .corr-row { grid-template-columns: 1fr; }
}
.forecast-card {
    background: #ffffff;
    border: 1px solid #c8ddf0;
    border-radius: 16px; padding: 1rem 0.5rem; text-align: center;
    box-shadow: 0 2px 8px rgba(30,80,160,0.07);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.forecast-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(26,107,196,0.14);
    border-color: #91c0f0;
}
.fc-day {
    font-size: 0.72rem; font-weight: 700; color: #1a6bc4;
    text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.45rem;
}
.fc-icon  { font-size: 1.6rem; margin-bottom: 0.35rem; }
.fc-label {
    font-size: 0.69rem; color: #5580a8; font-weight: 600;
    line-height: 1.3; min-height: 2.2em; margin-bottom: 0.45rem;
}
.fc-temp {
    font-size: 0.83rem; font-weight: 700; color: #0f2d56;
    font-family: 'Space Mono', monospace; margin-bottom: 0.2rem;
}
.fc-detail { font-size: 0.69rem; color: #7a9dc0; margin-bottom: 0.1rem; }

/* ── Condition badge ── */
.kondisi-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: #e0f0ff; border: 1px solid #91c0f0; color: #1252a3;
    font-size: 0.92rem; font-weight: 600;
    padding: 0.4rem 1.2rem; border-radius: 40px; margin-top: 0.6rem;
}

/* ── Prediction cards (LSTM page) ── */
.pred-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 0.65rem; margin-top: 0.5rem;
}
.pred-card {
    background: #ffffff; border: 1px solid #c8ddf0;
    border-radius: 16px; padding: 1.1rem 0.6rem; text-align: center;
    box-shadow: 0 2px 8px rgba(30,80,160,0.07);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.pred-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(26,107,196,0.14);
    border-color: #91c0f0;
}
.pred-day { font-size: 0.72rem; font-weight: 700; color: #1a6bc4; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.4rem; }
.pred-temp { font-size: 1.45rem; font-weight: 800; font-family: 'Space Mono', monospace; margin: 0.25rem 0; }
.pred-unit { font-size: 0.74rem; color: #5580a8; font-weight: 600; }
.pred-label { font-size: 0.68rem; color: #9ab8d8; margin-top: 0.25rem; }

/* ── Correlation cards ── */
.corr-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.2rem; }
.corr-card {
    background: #ffffff; border: 1px solid #c8ddf0;
    border-radius: 18px; padding: 1.4rem 1rem; text-align: center;
    box-shadow: 0 2px 12px rgba(30,80,160,0.07);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.corr-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(26,107,196,0.14);
    border-color: #91c0f0;
}
.corr-label { font-size: 0.77rem; color: #5580a8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem; }
.corr-value { font-size: 2.1rem; font-weight: 800; color: #0f2d56; font-family: 'Space Mono', monospace; }
.corr-sub { font-size: 0.71rem; color: #9ab8d8; margin-top: 0.3rem; }

/* ── Expander ── */
div[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #c8ddf0 !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 8px rgba(30,80,160,0.05);
}
div[data-testid="stExpander"] summary { color: #1a3a5c !important; font-weight: 600 !important; }

/* ── Slider ── */
[data-testid="stSlider"] label { color: #1a3a5c !important; font-weight: 600 !important; font-size: 0.9rem !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: transparent; }
.stTabs [data-baseweb="tab"] {
    background: #ffffff; border-radius: 10px; color: #5580a8;
    font-weight: 600; border: 1px solid #c8ddf0;
}
.stTabs [aria-selected="true"] {
    background: #1a6bc4 !important; color: #ffffff !important;
    border-color: #1a6bc4 !important;
}

/* ── Legend bar ── */
.legend-bar {
    display: flex; gap: 0.55rem; align-items: center;
    flex-wrap: wrap; margin-top: 0.6rem;
    font-size: 0.75rem; font-weight: 600;
}
.legend-item { padding: 3px 11px; border-radius: 20px; }

/* ── Footer ── */
.footer-bar {
    text-align: center; color: #8aabcc;
    font-size: 0.8rem; margin-top: 2.5rem;
    padding-top: 1rem; border-top: 1px solid #c8ddf0;
}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)


# =========================
# HELPER FUNCTIONS
# =========================
def weather_label(code: int) -> str:
    mapping = {
        0: "Cerah", 1: "Cerah Berawan", 2: "Berawan", 3: "Mendung",
        45: "Berkabut", 48: "Berkabut",
        51: "Gerimis Ringan", 53: "Gerimis", 55: "Gerimis Lebat",
        61: "Hujan Ringan", 63: "Hujan Sedang", 65: "Hujan Lebat",
        66: "Hujan Lebat", 67: "Hujan Lebat",
        71: "Hujan Lebat", 73: "Hujan Lebat", 75: "Hujan Lebat",
        77: "Cuaca Ekstrem",
        80: "Hujan Lokal Ringan", 81: "Hujan Lokal", 82: "Hujan Lokal Lebat",
        85: "Cuaca Ekstrem", 86: "Cuaca Ekstrem",
        95: "Badai Petir", 96: "Badai Petir", 99: "Badai Petir",
    }
    return mapping.get(int(code), "Tidak Diketahui")


def weather_icon(code: int) -> str:
    c = int(code)
    if c == 0:                      return "☀️"
    elif c == 1:                    return "🌤️"
    elif c == 2:                    return "⛅"
    elif c == 3:                    return "☁️"
    elif c in (45, 48):             return "🌫️"
    elif c in (51, 53, 55):         return "🌦️"
    elif c in (61, 63, 65, 66, 67): return "🌧️"
    elif c in (71, 73, 75, 77):     return "❄️"
    elif c in (80, 81, 82):         return "🌧️"
    elif c in (95, 96, 99):         return "⛈️"
    return "🌡️"


def get_marker_colors(suhu):
    if suhu is None:  return "#888888", "#aaaaaa"
    if suhu >= 35:    return "#e03030", "#f06060"
    if suhu >= 33:    return "#e07800", "#f0a030"
    if suhu >= 30:    return "#c8a000", "#e0c020"
    if suhu >= 27:    return "#1a6bc4", "#4090e0"
    return "#0099bb", "#30bbd8"


# =========================
# DATA FETCHING
# =========================
@st.cache_data(ttl=3600)
def get_live_weather():
    params = {
        "latitude": LAT_DEPOK, "longitude": LON_DEPOK,
        "current": ["temperature_2m", "relative_humidity_2m", "precipitation",
                    "wind_speed_10m", "weather_code"],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min",
                  "precipitation_sum", "wind_speed_10m_max"],
        "forecast_days": 7, "timezone": "Asia/Jakarta",
    }
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(data), encoding="utf-8")
        return data, "live"
    except Exception:
        if CACHE_FILE.exists():
            return json.loads(CACHE_FILE.read_text(encoding="utf-8")), "cache"
        return None, "error"


@st.cache_data(ttl=3600)
def get_kecamatan_weather():
    results = []
    for kec in KECAMATAN:
        params = {
            "latitude": kec["lat"], "longitude": kec["lon"],
            "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "weather_code"],
            "timezone": "Asia/Jakarta",
        }
        try:
            r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=15)
            r.raise_for_status()
            d = r.json()["current"]
            results.append({
                "nama": kec["nama"], "lat": kec["lat"], "lon": kec["lon"],
                "suhu": d["temperature_2m"], "kelembaban": d["relative_humidity_2m"],
                "hujan": d["precipitation"],
                "kondisi": weather_label(d["weather_code"]),
                "icon":    weather_icon(d["weather_code"]),
            })
        except Exception:
            results.append({
                "nama": kec["nama"], "lat": kec["lat"], "lon": kec["lon"],
                "suhu": None, "kelembaban": None, "hujan": None,
                "kondisi": "Data N/A", "icon": "❓",
            })
    return results


# =========================
# LOAD DATA
# =========================
live_data, live_source = get_live_weather()
kec_weather = get_kecamatan_weather()

# =========================
# HERO BANNER
# =========================
st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">🛰️ Real-time &middot; Open-Meteo API</div>
    <h1 class="hero-title">🌤️ Cuaca Kota Depok</h1>
    <p class="hero-sub">
        Dashboard pemantauan cuaca real-time berbasis model LSTM &mdash;
        kondisi terkini, prakiraan 7 hari, dan peta cuaca interaktif
        seluruh kecamatan Kota Depok secara otomatis.
    </p>
</div>
""", unsafe_allow_html=True)

if live_source == "cache":
    st.info("⚠️ API live sedang dibatasi — menampilkan data cache terakhir yang berhasil diambil.")
elif live_source == "error":
    st.warning("Data live tidak tersedia saat ini.")

# =========================
# KONDISI SAAT INI
# =========================
st.markdown('<div class="section-title">⚡ Kondisi Saat Ini</div>', unsafe_allow_html=True)

if live_data:
    cur = live_data["current"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌡️ Suhu",           f'{cur["temperature_2m"]:.1f} °C')
    c2.metric("💧 Kelembaban",      f'{cur["relative_humidity_2m"]:.0f} %')
    c3.metric("🌧️ Curah Hujan",    f'{cur["precipitation"]:.1f} mm')
    c4.metric("💨 Kecepatan Angin", f'{cur["wind_speed_10m"]:.1f} km/jam')

    icon_now  = weather_icon(cur["weather_code"])
    label_now = weather_label(cur["weather_code"])
    st.markdown(
        f'<div class="kondisi-badge">'
        f'{icon_now}&nbsp;&nbsp;Kondisi sekarang:&nbsp;<b>{label_now}</b>'
        f'</div>',
        unsafe_allow_html=True,
    )
else:
    st.write("Data cuaca live tidak tersedia saat ini.")

# =========================
# PRAKIRAAN 7 HARI
# =========================
st.markdown('<div class="section-title">📅 Prakiraan 7 Hari ke Depan</div>', unsafe_allow_html=True)

if live_data:
    daily = live_data["daily"]
    df_daily = pd.DataFrame({
        "tanggal": pd.to_datetime(daily["time"]),
        "code":  daily["weather_code"],
        "tmax":  daily["temperature_2m_max"],
        "tmin":  daily["temperature_2m_min"],
        "hujan": daily["precipitation_sum"],
        "angin": daily["wind_speed_10m_max"],
    })

    cards_html = '<div class="forecast-grid">'
    for _, row in df_daily.iterrows():
        hari  = row['tanggal'].strftime('%a')
        tgl   = row['tanggal'].strftime('%d %b')
        icon  = weather_icon(int(row['code']))
        label = weather_label(int(row['code']))
        cards_html += (
            '<div class="forecast-card">'
            f'<div class="fc-day">{hari}<br>'
            f'<span style="font-weight:400;color:#9ab8d8;font-size:0.66rem">{tgl}</span></div>'
            f'<div class="fc-icon">{icon}</div>'
            f'<div class="fc-label">{label}</div>'
            f'<div class="fc-temp">{row["tmin"]:.0f}° &ndash; {row["tmax"]:.0f}°</div>'
            f'<div class="fc-detail">🌧️ {row["hujan"]:.1f} mm</div>'
            f'<div class="fc-detail">💨 {row["angin"]:.0f} km/j</div>'
            '</div>'
        )
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

# =========================
# PETA CUACA PER KECAMATAN
# =========================
st.markdown('<div class="section-title">🗺️ Peta Cuaca Per Kecamatan</div>', unsafe_allow_html=True)

peta = folium.Map(
    location=[LAT_DEPOK, LON_DEPOK],
    zoom_start=12,
    tiles="CartoDB positron",   # peta terang, selaras tema
)

for kec in kec_weather:
    color, fill = get_marker_colors(kec['suhu'])
    suhu_str = f'{kec["suhu"]:.1f} °C'   if kec['suhu']       is not None else 'N/A'
    kel_str  = f'{kec["kelembaban"]:.0f} %' if kec['kelembaban'] is not None else 'N/A'
    huj_str  = f'{kec["hujan"]:.1f} mm'  if kec['hujan']      is not None else 'N/A'

    popup_html = (
        '<div style="font-family:Inter,sans-serif;background:#fff;color:#0f2d56;'
        'border-radius:12px;padding:12px 16px;min-width:210px;'
        'border:1px solid #c8ddf0;box-shadow:0 4px 16px rgba(30,80,160,0.12);">'
        f'<div style="font-size:1rem;font-weight:700;margin-bottom:4px;">'
        f'{kec["icon"]} Kec. {kec["nama"]}</div>'
        f'<div style="font-size:0.8rem;color:#1a6bc4;margin-bottom:10px;">{kec["kondisi"]}</div>'
        '<table style="width:100%;font-size:0.82rem;border-collapse:collapse;">'
        f'<tr><td style="color:#5580a8;padding:3px 0;">🌡️ Suhu</td>'
        f'<td style="text-align:right;font-weight:700;color:{color};">{suhu_str}</td></tr>'
        f'<tr><td style="color:#5580a8;padding:3px 0;">💧 Kelembaban</td>'
        f'<td style="text-align:right;font-weight:600;">{kel_str}</td></tr>'
        f'<tr><td style="color:#5580a8;padding:3px 0;">🌧️ Hujan</td>'
        f'<td style="text-align:right;font-weight:600;">{huj_str}</td></tr>'
        '</table></div>'
    )

    folium.CircleMarker(
        location=[kec['lat'], kec['lon']],
        radius=20, color=color, fill=True, fill_color=fill,
        fill_opacity=0.55, weight=2.5,
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"<b>{kec['nama']}</b> · {kec['icon']} {kec['kondisi']} · {suhu_str}",
    ).add_to(peta)

    folium.Marker(
        location=[kec['lat'], kec['lon']],
        icon=folium.DivIcon(
            html=(
                '<div style="font-family:Inter,sans-serif;font-size:9px;font-weight:700;'
                'color:#0f2d56;text-shadow:0 1px 2px rgba(255,255,255,0.9);'
                'text-align:center;white-space:nowrap;'
                f'margin-top:-6px;margin-left:-35px;">{kec["nama"]}</div>'
            ),
            icon_size=(90, 18), icon_anchor=(0, 0),
        ),
    ).add_to(peta)

st_folium(peta, use_container_width=True, height=500)

st.markdown("""
<div class="legend-bar">
    <span style="color:#5580a8;">Legenda suhu:</span>
    <span class="legend-item" style="background:#fde8e8;color:#b02020;border:1px solid #f0b0b0;">&ge;35°C — Sangat Panas</span>
    <span class="legend-item" style="background:#fff0dd;color:#b06000;border:1px solid #f0c870;">33–35°C — Panas</span>
    <span class="legend-item" style="background:#fffacc;color:#8a7000;border:1px solid #e0d060;">30–33°C — Hangat</span>
    <span class="legend-item" style="background:#ddeeff;color:#1252a3;border:1px solid #91c0f0;">27–30°C — Sejuk</span>
    <span class="legend-item" style="background:#ccf5ff;color:#006888;border:1px solid #70d8f0;">&lt;27°C — Dingin</span>
</div>
""", unsafe_allow_html=True)

with st.expander("📋 Ringkasan data semua kecamatan"):
    df_kec = pd.DataFrame([{
        "Kecamatan":      k["nama"],
        "Suhu (°C)":      round(k["suhu"], 1)    if k["suhu"]       is not None else "N/A",
        "Kelembaban (%)": round(k["kelembaban"])  if k["kelembaban"] is not None else "N/A",
        "Hujan (mm)":     round(k["hujan"], 1)   if k["hujan"]      is not None else "N/A",
        "Kondisi":        f'{k["icon"]} {k["kondisi"]}',
    } for k in kec_weather])
    st.dataframe(df_kec, use_container_width=True, hide_index=True)

st.markdown(
    f'<div class="footer-bar">'
    f'📍 Kota Depok · {LAT_DEPOK}°S, {LON_DEPOK}°E '
    f'· Sumber: Open-Meteo API · 11 Kecamatan</div>',
    unsafe_allow_html=True,
)
