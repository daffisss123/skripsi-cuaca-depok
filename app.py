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
    {"nama": "Beji", "lat": -6.3750, "lon": 106.8300},
    {"nama": "Bojongsari", "lat": -6.4400, "lon": 106.7500},
    {"nama": "Cilodong", "lat": -6.4100, "lon": 106.8400},
    {"nama": "Cimanggis", "lat": -6.3700, "lon": 106.8800},
    {"nama": "Cinere", "lat": -6.3600, "lon": 106.7800},
    {"nama": "Cipayung", "lat": -6.4300, "lon": 106.8600},
    {"nama": "Limo", "lat": -6.3900, "lon": 106.7700},
    {"nama": "Pancoran Mas", "lat": -6.4000, "lon": 106.8200},
    {"nama": "Sawangan", "lat": -6.4500, "lon": 106.7700},
    {"nama": "Sukmajaya", "lat": -6.3800, "lon": 106.8500},
    {"nama": "Tapos", "lat": -6.3600, "lon": 106.8900},
]

# =========================
# STYLE PREMIUM - LIGHT CLEAN
# =========================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Mono:wght@700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.stApp {
    background: linear-gradient(160deg, #f0f4ff 0%, #e8f0fe 50%, #f5f7ff 100%);
    min-height: 100vh;
}
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.97) !important;
    border-right: 1px solid rgba(99,130,255,0.12);
    box-shadow: 2px 0 16px rgba(99,130,255,0.07);
}
.hero-banner {
    background: linear-gradient(135deg, #4f8ef7 0%, #2563eb 60%, #1d4ed8 100%);
    border-radius: 24px;
    padding: 2.2rem 2.4rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(37,99,235,0.22);
}
.hero-banner::before {
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(255,255,255,0.13) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-banner::after {
    content: "";
    position: absolute;
    bottom: -40px; left: 40%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.22);
    border: 1px solid rgba(255,255,255,0.38);
    color: #fff;
    font-size: 0.73rem;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    padding: 0.26rem 0.75rem;
    border-radius: 20px;
    margin-bottom: 0.9rem;
}
.hero-title {
    font-size: 2.35rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.45rem 0;
    letter-spacing: -0.5px;
}
.hero-sub {
    color: rgba(255,255,255,0.82);
    font-size: 0.97rem;
    margin: 0;
    line-height: 1.65;
    max-width: 640px;
}
.section-title {
    font-size: 1.08rem;
    font-weight: 700;
    color: #1e3a5f;
    margin: 1.8rem 0 0.9rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-title::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(37,99,235,0.2), transparent);
    margin-left: 0.4rem;
}
div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid rgba(99,130,255,0.15) !important;
    border-radius: 18px !important;
    padding: 1.15rem 1rem !important;
    box-shadow: 0 2px 12px rgba(37,99,235,0.07);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(37,99,235,0.14) !important;
}
div[data-testid="stMetric"] label {
    color: #5b7ba8 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #1e3a5f !important;
    font-size: 1.82rem !important;
    font-weight: 700 !important;
    font-family: 'Space Mono', monospace !important;
}
.kondisi-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
    font-size: 0.92rem;
    font-weight: 600;
    padding: 0.42rem 1.2rem;
    border-radius: 40px;
    margin-top: 0.7rem;
}
.forecast-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 0.65rem;
    margin-top: 0.4rem;
}
.forecast-card {
    background: #ffffff;
    border: 1px solid rgba(99,130,255,0.13);
    border-radius: 18px;
    padding: 1rem 0.55rem;
    text-align: center;
    box-shadow: 0 2px 10px rgba(37,99,235,0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.forecast-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 28px rgba(37,99,235,0.13);
    border-color: rgba(37,99,235,0.22);
}
/* Hourly forecast */
.hourly-scroll {
    display: flex;
    gap: 0.55rem;
    overflow-x: auto;
    padding-bottom: 0.6rem;
    margin-top: 0.4rem;
    scrollbar-width: thin;
    scrollbar-color: rgba(37,99,235,0.2) transparent;
}
.hourly-scroll::-webkit-scrollbar { height: 5px; }
.hourly-scroll::-webkit-scrollbar-thumb {
    background: rgba(37,99,235,0.2); border-radius: 10px;
}
.hourly-card {
    background: #ffffff;
    border: 1px solid rgba(99,130,255,0.13);
    border-radius: 16px;
    padding: 0.85rem 0.6rem;
    text-align: center;
    min-width: 72px;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(37,99,235,0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.hourly-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 22px rgba(37,99,235,0.13);
    border-color: rgba(37,99,235,0.22);
}
.hourly-card.is-now {
    background: linear-gradient(135deg,#eff6ff,#dbeafe);
    border-color: #93c5fd;
}
.hc-time { font-size: 0.72rem; font-weight: 700; color: #2563eb; margin-bottom: 0.35rem; }
.hc-icon { font-size: 1.5rem; margin-bottom: 0.3rem; }
.hc-temp { font-size: 0.82rem; font-weight: 700; color: #1e3a5f; font-family: 'Space Mono',monospace; margin-bottom: 0.15rem; }
.hc-rain { font-size: 0.68rem; color: #94a3b8; }
/* Live clock inside hero */
.hero-clock {
    font-family: 'Space Mono', monospace;
    font-size: 1.55rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.04em;
    margin-top: 0.55rem;
}
.hero-clock-date {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.72);
    margin-top: 0.1rem;
    font-weight: 500;
}
.fc-day {
    font-size: 0.73rem;
    font-weight: 700;
    color: #2563eb;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.5rem;
}
.fc-icon  { font-size: 1.65rem; margin-bottom: 0.4rem; }
.fc-label {
    font-size: 0.7rem;
    color: #5b7ba8;
    font-weight: 600;
    margin-bottom: 0.5rem;
    line-height: 1.3;
    min-height: 2.2em;
}
.fc-temp {
    font-size: 0.85rem;
    font-weight: 700;
    color: #1e3a5f;
    font-family: 'Space Mono', monospace;
    margin-bottom: 0.22rem;
}
.fc-detail { font-size: 0.7rem; color: #94a3b8; margin-bottom: 0.12rem; }
.legend-bar {
    display: flex;
    gap: 0.6rem;
    align-items: center;
    flex-wrap: wrap;
    margin-top: 0.6rem;
    font-size: 0.76rem;
    font-weight: 600;
}
.legend-item { padding: 3px 12px; border-radius: 20px; }
.footer-bar {
    text-align: center;
    color: #94a3b8;
    font-size: 0.8rem;
    margin-top: 2.5rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(99,130,255,0.12);
}
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: transparent; }
.stTabs [data-baseweb="tab"] {
    background: #ffffff;
    border-radius: 10px;
    color: #5b7ba8;
    font-weight: 600;
    border: 1px solid rgba(99,130,255,0.13);
}
.stTabs [aria-selected="true"] {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    border-color: #bfdbfe !important;
}
header[data-testid="stHeader"] {
    background: rgba(240,244,255,0.97) !important;
    backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(99,130,255,0.1);
}
header[data-testid="stHeader"]::before { background: transparent !important; }
header[data-testid="stHeader"] button,
header[data-testid="stHeader"] a { color: #2563eb !important; }
header[data-testid="stHeader"] svg { fill: #2563eb !important; }
[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid rgba(99,130,255,0.13) !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.05);
}
div[data-testid="stExpander"] summary { color: #2563eb !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)


# =========================
# HELPER FUNCTIONS
# =========================
def weather_label(code: int) -> str:
    mapping = {
        0: "Cerah",
        1: "Cerah Berawan",
        2: "Berawan",
        3: "Mendung",
        45: "Berkabut",
        48: "Berkabut",
        51: "Gerimis Ringan",
        53: "Gerimis",
        55: "Gerimis Lebat",
        61: "Hujan Ringan",
        63: "Hujan Sedang",
        65: "Hujan Lebat",
        66: "Hujan Lebat",
        67: "Hujan Lebat",
        71: "Hujan Lebat",
        73: "Hujan Lebat",
        75: "Hujan Lebat",
        77: "Cuaca Ekstrem",
        80: "Hujan Lokal Ringan",
        81: "Hujan Lokal",
        82: "Hujan Lokal Lebat",
        85: "Cuaca Ekstrem",
        86: "Cuaca Ekstrem",
        95: "Badai Petir",
        96: "Badai Petir",
        99: "Badai Petir",
    }
    return mapping.get(int(code), "Tidak Diketahui")


def weather_icon(code: int) -> str:
    c = int(code)
    if c == 0:                        return "☀️"
    elif c == 1:                      return "🌤️"
    elif c == 2:                      return "⛅"
    elif c == 3:                      return "☁️"
    elif c in (45, 48):               return "🌫️"
    elif c in (51, 53, 55):           return "🌦️"
    elif c in (61, 63, 65, 66, 67):   return "🌧️"
    elif c in (71, 73, 75, 77):       return "❄️"
    elif c in (80, 81, 82):           return "🌧️"
    elif c in (95, 96, 99):           return "⛈️"
    return "🌡️"


def get_marker_colors(suhu):
    if suhu is None:  return "#888888", "#aaaaaa"
    if suhu >= 35:    return "#ef4444", "#fca5a5"
    if suhu >= 33:    return "#f97316", "#fdba74"
    if suhu >= 30:    return "#eab308", "#fde047"
    if suhu >= 27:    return "#2563eb", "#93c5fd"
    return "#06b6d4", "#67e8f9"


# =========================
# DATA FETCHING
# =========================
_WEATHER_PARAMS = {
    "latitude":  LAT_DEPOK,
    "longitude": LON_DEPOK,
    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "weather_code",
    ],
    "daily": [
        "weather_code",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "wind_speed_10m_max",
    ],
    "hourly": [
        "temperature_2m",
        "precipitation",
        "weather_code",
    ],
    "forecast_days": 7,
    "timezone": "Asia/Jakarta",
}

# Tidak di-cache agar selalu fresh saat dipanggil langsung
def _fetch_live_weather():
    r = requests.get("https://api.open-meteo.com/v1/forecast", params=_WEATHER_PARAMS, timeout=30)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=1800, show_spinner="Mengambil data cuaca...")
def get_live_weather():
    try:
        data = _fetch_live_weather()
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(data), encoding="utf-8")
        return data, "live"
    except Exception as e:
        # Jika gagal, jangan simpan error ke cache
        # Coba baca dari file cache lokal
        if CACHE_FILE.exists():
            try:
                return json.loads(CACHE_FILE.read_text(encoding="utf-8")), "cache"
            except Exception:
                pass
        return None, "error"


@st.cache_data(ttl=1800, show_spinner="Mengambil data kecamatan...")
def get_kecamatan_weather():
    results = []
    for kec in KECAMATAN:
        params = {
            "latitude":  kec["lat"],
            "longitude": kec["lon"],
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "weather_code",
            ],
            "timezone": "Asia/Jakarta",
        }
        try:
            r = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params=params,
                timeout=15,
            )
            r.raise_for_status()
            d = r.json()["current"]
            results.append({
                "nama":       kec["nama"],
                "lat":        kec["lat"],
                "lon":        kec["lon"],
                "suhu":       d["temperature_2m"],
                "kelembaban": d["relative_humidity_2m"],
                "hujan":      d["precipitation"],
                "kondisi":    weather_label(d["weather_code"]),
                "icon":       weather_icon(d["weather_code"]),
            })
        except Exception:
            results.append({
                "nama":       kec["nama"],
                "lat":        kec["lat"],
                "lon":        kec["lon"],
                "suhu":       None,
                "kelembaban": None,
                "hujan":      None,
                "kondisi":    "Data N/A",
                "icon":       "❓",
            })
    return results


# =========================
# LOAD DATA
# =========================
# Tombol refresh di sidebar
with st.sidebar:
    st.markdown("---")
    if st.button("🔄 Refresh Data Cuaca", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption("Data diperbarui otomatis setiap 30 menit.")

live_data, live_source = get_live_weather()
kec_weather = get_kecamatan_weather()


# =========================
# HERO BANNER
# =========================
st.markdown("""
<div class="hero-banner">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
        <div>
            <div class="hero-badge">🛰️ Real-time &middot; Open-Meteo API</div>
            <h1 class="hero-title">🌤️ Cuaca Kota Depok</h1>
            <p class="hero-sub">
                Dashboard pemantauan cuaca real-time berbasis model LSTM &mdash;
                kondisi terkini, prakiraan 7 hari, dan peta cuaca interaktif
                seluruh kecamatan Kota Depok secara otomatis.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Live clock via st.markdown + srcdoc iframe (kompatibel semua versi Streamlit)
import base64, datetime as _dt
_clock_html = """<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@700&family=Plus+Jakarta+Sans:wght@500;600&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: transparent; display: flex; justify-content: center; align-items: center; min-height: 80px; }
  .clock-wrap {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 50%, #3b82f6 100%);
    border-radius: 20px;
    padding: 14px 28px;
    display: inline-flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 4px 24px rgba(37,99,235,0.35);
    border: 1px solid rgba(255,255,255,0.18);
  }
  .clock-icon { font-size: 2rem; line-height: 1; }
  .clock-right { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; }
  .clock-time {
    font-family: 'Space Mono', monospace;
    font-size: 1.85rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.04em;
    line-height: 1;
  }
  .clock-time .colon {
    animation: blink 1s step-start infinite;
    display: inline-block;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
  .clock-wib {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.6);
    letter-spacing: 0.12em;
    margin-left: 2px;
  }
  .clock-date {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.78);
    font-weight: 500;
    letter-spacing: 0.01em;
  }
</style>
</head>
<body>
<div class="clock-wrap">
  <div class="clock-icon">🕐</div>
  <div class="clock-right">
    <div class="clock-time">
      <span id="hh">--</span><span class="colon">:</span><span id="mm">--</span><span class="colon">:</span><span id="ss">--</span>
      <span class="clock-wib">WIB</span>
    </div>
    <div class="clock-date" id="tgl">Memuat...</div>
  </div>
</div>
<script>
const HARI   = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'];
const BULAN  = ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'];
function pad(n){ return String(n).padStart(2,'0'); }
function tick(){
  const now = new Date();
  document.getElementById('hh').textContent = pad(now.getHours());
  document.getElementById('mm').textContent = pad(now.getMinutes());
  document.getElementById('ss').textContent = pad(now.getSeconds());
  document.getElementById('tgl').textContent =
    HARI[now.getDay()] + ', ' + now.getDate() + ' ' + BULAN[now.getMonth()] + ' ' + now.getFullYear();
}
tick();
setInterval(tick, 1000);
</script>
</body>
</html>"""
_b64 = base64.b64encode(_clock_html.encode()).decode()
st.markdown(
    f'<iframe src="data:text/html;base64,{_b64}" '
    f'style="width:100%;height:90px;border:none;background:transparent;" '
    f'scrolling="no"></iframe>',
    unsafe_allow_html=True,
)


if live_source == "cache":
    st.info("⚠️ API live sedang dibatasi — menampilkan data cache terakhir yang berhasil diambil.")
elif live_source == "error":
    st.warning(
        "🚫 Data live tidak tersedia saat ini. "
        "Pastikan perangkat terhubung ke internet dan API Open-Meteo dapat diakses. "
        "Data akan ditampilkan otomatis saat koneksi pulih."
    )


# =========================
# KONDISI SAAT INI
# =========================
st.markdown('<div class="section-title">⚡ Kondisi Saat Ini</div>', unsafe_allow_html=True)

if live_data and "current" in live_data:
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
    st.info("⚠️ Data cuaca live tidak tersedia. Coba muat ulang halaman setelah beberapa saat.")


# =========================
# PRAKIRAAN PER JAM
# =========================
st.markdown('<div class="section-title">🕐 Prakiraan 24 Jam ke Depan</div>', unsafe_allow_html=True)

if not live_data:
    st.info("⚠️ Prakiraan 24 jam tidak tersedia — tidak ada koneksi ke API dan tidak ada data cache.")
elif "hourly" not in live_data:
    st.info("⚠️ Data prakiraan per jam tidak tersedia dalam respons API.")
else:
    import datetime
    hourly = live_data["hourly"]
    df_hourly = pd.DataFrame({
        "waktu": pd.to_datetime(hourly["time"]),
        "suhu":  hourly["temperature_2m"],
        "hujan": hourly["precipitation"],
        "code":  hourly["weather_code"],
    })
    # Ambil jam sekarang (WIB = UTC+7)
    now_wib = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    # Filter mulai dari jam terdekat, ambil 24 jam ke depan
    df_upcoming = df_hourly[df_hourly["waktu"] >= now_wib.replace(minute=0, second=0, microsecond=0)].head(24)

    cards_h = '<div class="hourly-scroll">'
    first = True
    for _, row in df_upcoming.iterrows():
        jam   = row["waktu"].strftime("%H:%M")
        icon  = weather_icon(int(row["code"]))
        now_cls = ' is-now' if first else ''
        first = False
        cards_h += (
            f'<div class="hourly-card{now_cls}">'
            f'<div class="hc-time">{jam}</div>'
            f'<div class="hc-icon">{icon}</div>'
            f'<div class="hc-temp">{row["suhu"]:.0f}°</div>'
            f'<div class="hc-rain">🌧️ {row["hujan"]:.1f}mm</div>'
            '</div>'
        )
    cards_h += '</div>'
    st.markdown(cards_h, unsafe_allow_html=True)


# =========================
# PRAKIRAAN 7 HARI
# =========================
st.markdown('<div class="section-title">📅 Prakiraan 7 Hari ke Depan</div>', unsafe_allow_html=True)

if not live_data:
    st.info("⚠️ Prakiraan 7 hari tidak tersedia — tidak ada koneksi ke API dan tidak ada data cache.")
elif "daily" not in live_data:
    st.info("⚠️ Data prakiraan harian tidak tersedia dalam respons API.")
else:
    daily = live_data["daily"]
    df_daily = pd.DataFrame({
        "tanggal": pd.to_datetime(daily["time"]),
        "code":    daily["weather_code"],
        "tmax":    daily["temperature_2m_max"],
        "tmin":    daily["temperature_2m_min"],
        "hujan":   daily["precipitation_sum"],
        "angin":   daily["wind_speed_10m_max"],
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
            f'<span style="font-weight:400;color:#94a3b8;font-size:0.67rem">{tgl}</span></div>'
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
    tiles="CartoDB positron",
)

for kec in kec_weather:
    color, fill = get_marker_colors(kec['suhu'])

    suhu_str = f'{kec["suhu"]:.1f} °C' if kec['suhu'] is not None else 'N/A'
    kel_str  = f'{kec["kelembaban"]:.0f} %' if kec['kelembaban'] is not None else 'N/A'
    huj_str  = f'{kec["hujan"]:.1f} mm' if kec['hujan'] is not None else 'N/A'

    popup_html = (
        '<div style="font-family:sans-serif;background:#ffffff;color:#1e3a5f;'
        'border-radius:12px;padding:12px 16px;min-width:210px;'
        'border:1px solid rgba(37,99,235,0.15);box-shadow:0 4px 16px rgba(37,99,235,0.1);">'
        f'<div style="font-size:1rem;font-weight:700;margin-bottom:4px;">'
        f'{kec["icon"]} Kec. {kec["nama"]}</div>'
        f'<div style="font-size:0.8rem;color:#2563eb;margin-bottom:10px;">{kec["kondisi"]}</div>'
        '<table style="width:100%;font-size:0.82rem;border-collapse:collapse;">'
        f'<tr><td style="color:#94a3b8;padding:3px 0;">🌡️ Suhu</td>'
        f'<td style="text-align:right;font-weight:700;color:{color};">{suhu_str}</td></tr>'
        f'<tr><td style="color:#94a3b8;padding:3px 0;">💧 Kelembaban</td>'
        f'<td style="text-align:right;font-weight:600;">{kel_str}</td></tr>'
        f'<tr><td style="color:#94a3b8;padding:3px 0;">🌧️ Hujan</td>'
        f'<td style="text-align:right;font-weight:600;">{huj_str}</td></tr>'
        '</table></div>'
    )

    folium.CircleMarker(
        location=[kec['lat'], kec['lon']],
        radius=20,
        color=color,
        fill=True,
        fill_color=fill,
        fill_opacity=0.55,
        weight=2.5,
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"<b>{kec['nama']}</b> · {kec['icon']} {kec['kondisi']} · {suhu_str}",
    ).add_to(peta)

    folium.Marker(
        location=[kec['lat'], kec['lon']],
        icon=folium.DivIcon(
            html=(
                '<div style="font-family:sans-serif;font-size:9px;font-weight:700;'
                'color:#1e3a5f;text-shadow:0 1px 3px rgba(255,255,255,0.9);'
                'text-align:center;white-space:nowrap;'
                f'margin-top:-6px;margin-left:-35px;">{kec["nama"]}</div>'
            ),
            icon_size=(90, 18),
            icon_anchor=(0, 0),
        ),
    ).add_to(peta)

st_folium(peta, use_container_width=True, height=500)

st.markdown("""
<div class="legend-bar">
    <span style="color:#64748b;">Legenda suhu:</span>
    <span class="legend-item" style="background:#ef4444;color:#fff;">&ge;35&deg;C &mdash; Sangat Panas</span>
    <span class="legend-item" style="background:#f97316;color:#fff;">33&ndash;35&deg;C &mdash; Panas</span>
    <span class="legend-item" style="background:#eab308;color:#111;">30&ndash;33&deg;C &mdash; Hangat</span>
    <span class="legend-item" style="background:#2563eb;color:#fff;">27&ndash;30&deg;C &mdash; Sejuk</span>
    <span class="legend-item" style="background:#06b6d4;color:#fff;">&lt;27&deg;C &mdash; Dingin</span>
</div>
""", unsafe_allow_html=True)

with st.expander("📋 Ringkasan data semua kecamatan"):
    df_kec = pd.DataFrame([
        {
            "Kecamatan":       k["nama"],
            "Suhu (°C)":      round(k["suhu"], 1) if k["suhu"] is not None else "N/A",
            "Kelembaban (%)":  round(k["kelembaban"]) if k["kelembaban"] is not None else "N/A",
            "Hujan (mm)":      round(k["hujan"], 1) if k["hujan"] is not None else "N/A",
            "Kondisi":         f'{k["icon"]} {k["kondisi"]}',
        }
        for k in kec_weather
    ])
    st.dataframe(df_kec, use_container_width=True, hide_index=True)

# =========================
# FOOTER
# =========================
st.markdown(
    f'<div class="footer-bar">'
    f'📍 Kota Depok &middot; {LAT_DEPOK}°S, {LON_DEPOK}°E '
    f'&middot; Sumber: Open-Meteo API &middot; 11 Kecamatan</div>',
    unsafe_allow_html=True,
)    
