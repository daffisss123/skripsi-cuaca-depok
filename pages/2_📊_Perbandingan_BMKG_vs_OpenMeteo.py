import pandas as pd
import streamlit as st

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="Perbandingan BMKG vs Open-Meteo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# STYLE
# =========================
STYLE = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:wght@700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(150deg, #eef4fb 0%, #ddeaf8 50%, #e8f1fa 100%); min-height: 100vh; }
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #d4e2f0 !important; box-shadow: 2px 0 12px rgba(30,80,160,0.06); }
[data-testid="stSidebar"] * { color: #2c4a6e !important; }
header[data-testid="stHeader"] { background: rgba(238,244,251,0.92) !important; backdrop-filter: blur(8px); border-bottom: 1px solid #c8ddf0; }
header[data-testid="stHeader"]::before { background: transparent !important; }
header[data-testid="stHeader"] button, header[data-testid="stHeader"] a, header[data-testid="stHeader"] svg { color: #2c4a6e !important; fill: #2c4a6e !important; }
[data-testid="stDecoration"] { display: none !important; }
.page-header {
    background: linear-gradient(135deg, #1a6bc4 0%, #1252a3 100%);
    border-radius: 20px; padding: 2rem 2.4rem; margin-bottom: 1.8rem;
    position: relative; overflow: hidden; box-shadow: 0 8px 32px rgba(26,107,196,0.22);
}
.page-header::before {
    content: ""; position: absolute; top: -80px; right: -80px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
    border-radius: 50%; pointer-events: none;
}
.page-badge {
    display: inline-block; background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.35); color: #e0f0ff;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase;
    padding: 0.25rem 0.8rem; border-radius: 20px; margin-bottom: 0.8rem;
}
.page-title { font-size: 2.1rem; font-weight: 800; color: #fff; margin: 0 0 0.4rem; letter-spacing: -0.5px; }
.page-sub { color: rgba(255,255,255,0.82); font-size: 0.95rem; line-height: 1.65; max-width: 640px; margin: 0; }
.section-title {
    font-size: 1.05rem; font-weight: 700; color: #1a3a5c;
    margin: 1.8rem 0 0.85rem; display: flex; align-items: center; gap: 0.45rem;
}
.section-title::after {
    content: ""; flex: 1; height: 2px;
    background: linear-gradient(90deg, #b8d4f0, transparent);
    margin-left: 0.4rem; border-radius: 2px;
}
div[data-testid="stMetric"] {
    background: #ffffff !important; border: 1px solid #c8ddf0 !important;
    border-radius: 16px !important; padding: 1.1rem 1rem !important;
    box-shadow: 0 2px 12px rgba(30,80,160,0.07);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
div[data-testid="stMetric"]:hover { transform: translateY(-3px); box-shadow: 0 6px 24px rgba(26,107,196,0.14) !important; }
div[data-testid="stMetric"] label { color: #5580a8 !important; font-size: 0.76rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #0f2d56 !important; font-size: 1.7rem !important; font-weight: 700 !important; font-family: 'Space Mono', monospace !important; }
.info-card {
    background: #e8f3ff; border: 1px solid #b8d4f0; border-left: 4px solid #1a6bc4;
    border-radius: 12px; padding: 0.9rem 1.2rem; color: #1a3a5c;
    font-size: 0.88rem; line-height: 1.6; margin-bottom: 1rem;
}
.corr-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.2rem; }
.corr-card {
    background: #ffffff; border: 1px solid #c8ddf0; border-radius: 18px;
    padding: 1.4rem 1rem; text-align: center;
    box-shadow: 0 2px 12px rgba(30,80,160,0.07);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.corr-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(26,107,196,0.14); border-color: #91c0f0; }
.corr-label { font-size: 0.77rem; color: #5580a8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem; }
.corr-value { font-size: 2.1rem; font-weight: 800; color: #0f2d56; font-family: 'Space Mono', monospace; }
.corr-sub { font-size: 0.71rem; color: #9ab8d8; margin-top: 0.3rem; }
div[data-testid="stExpander"] { background: #ffffff !important; border: 1px solid #c8ddf0 !important; border-radius: 14px !important; box-shadow: 0 2px 8px rgba(30,80,160,0.05); }
div[data-testid="stExpander"] summary { color: #1a3a5c !important; font-weight: 600 !important; }
.footer-bar { text-align:center; color:#8aabcc; font-size:0.8rem; margin-top:2.5rem; padding-top:1rem; border-top:1px solid #c8ddf0; }
@media (max-width: 560px) { .page-title { font-size: 1.5rem; } .corr-row { grid-template-columns: 1fr; } .corr-value { font-size: 1.7rem; } }
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_compare_data():
    df_bmkg = pd.read_csv("data/processed/bmkg_2024_2026_final.csv")
    df_open = pd.read_csv("data/processed/openmeteo_overlap_2024_2026.csv")
    df_bmkg["tanggal"] = pd.to_datetime(df_bmkg["tanggal"])
    df_open["tanggal"] = pd.to_datetime(df_open["tanggal"])
    if "TAVG_openmeteo" not in df_open.columns:
        df_open["TAVG_openmeteo"] = (
            df_open["temperature_2m_max"] + df_open["temperature_2m_min"]
        ) / 2
    df = pd.merge(
        df_bmkg[["tanggal", "TAVG", "RR"]],
        df_open[["tanggal", "TAVG_openmeteo", "precipitation_sum"]],
        on="tanggal", how="inner"
    )
    return df.sort_values("tanggal").reset_index(drop=True)

df_compare = load_compare_data()

# =========================
# HEADER
# =========================
st.markdown("""
<div class="page-header">
    <div class="page-badge">📊 Analisis Data &middot; 2024&ndash;2026</div>
    <h1 class="page-title">BMKG vs Open-Meteo</h1>
    <p class="page-sub">
        Perbandingan konsistensi data suhu dan curah hujan antara
        stasiun BMKG dengan sumber data Open-Meteo pada periode yang sama.
    </p>
</div>
""", unsafe_allow_html=True)

# =========================
# INFO CARD
# =========================
n_data    = len(df_compare)
tgl_awal  = df_compare["tanggal"].min().strftime("%d %b %Y")
tgl_akhir = df_compare["tanggal"].max().strftime("%d %b %Y")
st.markdown(
    f'<div class="info-card">'
    f'📆 Dataset overlap: <b>{n_data} hari</b> '
    f'({tgl_awal} &ndash; {tgl_akhir})</div>',
    unsafe_allow_html=True,
)

# =========================
# KORELASI
# =========================
st.markdown('<div class="section-title">🔗 Korelasi Data</div>', unsafe_allow_html=True)

corr_temp = df_compare["TAVG"].corr(df_compare["TAVG_openmeteo"])
corr_rain = df_compare["RR"].corr(df_compare["precipitation_sum"])

def corr_label(r):
    if r >= 0.95:   return "Sangat Tinggi ✅"
    elif r >= 0.85: return "Tinggi 🟢"
    elif r >= 0.70: return "Sedang 🟡"
    return "Rendah 🔴"

st.markdown(
    '<div class="corr-row">'
    '<div class="corr-card">'
    '<div class="corr-label">🌡️ Korelasi Suhu</div>'
    f'<div class="corr-value">{corr_temp:.3f}</div>'
    '<div class="corr-sub">BMKG TAVG vs Open-Meteo TAVG</div>'
    f'<div class="corr-sub" style="margin-top:0.4rem;color:#1a6bc4;font-weight:600;">{corr_label(corr_temp)}</div>'
    '</div>'
    '<div class="corr-card">'
    '<div class="corr-label">🌧️ Korelasi Curah Hujan</div>'
    f'<div class="corr-value">{corr_rain:.3f}</div>'
    '<div class="corr-sub">BMKG RR vs Open-Meteo precipitation</div>'
    f'<div class="corr-sub" style="margin-top:0.4rem;color:#1a6bc4;font-weight:600;">{corr_label(corr_rain)}</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
col1.metric('Rata-rata Suhu BMKG',       f'{df_compare["TAVG"].mean():.1f} °C')
col2.metric('Rata-rata Suhu Open-Meteo', f'{df_compare["TAVG_openmeteo"].mean():.1f} °C')
col3.metric('Rata-rata Hujan BMKG',      f'{df_compare["RR"].mean():.1f} mm')
col4.metric('Rata-rata Hujan Open-Meteo',f'{df_compare["precipitation_sum"].mean():.1f} mm')

# =========================
# GRAFIK SUHU
# =========================
st.markdown('<div class="section-title">🌡️ Perbandingan Suhu Rata-rata Harian</div>', unsafe_allow_html=True)
chart_suhu = (
    df_compare[["tanggal", "TAVG", "TAVG_openmeteo"]]
    .copy().set_index("tanggal")
    .rename(columns={"TAVG": "BMKG", "TAVG_openmeteo": "Open-Meteo"})
)
st.line_chart(chart_suhu, color=["#e07800", "#1a6bc4"])

# =========================
# GRAFIK HUJAN
# =========================
st.markdown('<div class="section-title">🌧️ Perbandingan Curah Hujan Harian</div>', unsafe_allow_html=True)
chart_hujan = (
    df_compare[["tanggal", "RR", "precipitation_sum"]]
    .copy().set_index("tanggal")
    .rename(columns={"RR": "BMKG", "precipitation_sum": "Open-Meteo"})
)
st.line_chart(chart_hujan, color=["#e07800", "#1a6bc4"])

# =========================
# TABEL DATA TERBARU
# =========================
with st.expander("📋 Lihat data perbandingan terbaru (20 hari)"):
    df_show = df_compare.tail(20).copy()
    df_show["tanggal"] = df_show["tanggal"].dt.strftime("%d %b %Y")
    df_show.columns = ["Tanggal", "Suhu BMKG (°C)", "Hujan BMKG (mm)", "Suhu OM (°C)", "Hujan OM (mm)"]
    st.dataframe(df_show, use_container_width=True, hide_index=True)

st.markdown(
    '<div class="footer-bar">Sumber: BMKG &amp; Open-Meteo API &middot; Skripsi Prediksi Cuaca Kota Depok</div>',
    unsafe_allow_html=True,
)
