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
# STYLE — selaras dengan homepage
# =========================
STYLE = '''
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Mono:wght@700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: linear-gradient(160deg, #0d1b2a 0%, #1b2d45 40%, #0f2337 100%); min-height: 100vh; }
[data-testid="stSidebar"] { background: rgba(10,20,35,0.97) !important; border-right: 1px solid rgba(255,255,255,0.06); }
.page-header {
    background: linear-gradient(135deg, rgba(30,80,160,0.5) 0%, rgba(14,42,90,0.68) 100%);
    border: 1px solid rgba(100,160,255,0.22); border-radius: 24px;
    padding: 1.8rem 2.2rem; margin-bottom: 1.8rem;
    position: relative; overflow: hidden; backdrop-filter: blur(8px);
}
.page-header::before {
    content: ""; position: absolute; top: -60px; right: -60px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(56,152,255,0.14) 0%, transparent 70%);
    border-radius: 50%; pointer-events: none;
}
.page-badge {
    display: inline-block; background: rgba(56,152,255,0.18);
    border: 1px solid rgba(56,152,255,0.38); color: #7ec8ff;
    font-size: 0.73rem; font-weight: 600; letter-spacing: 0.09em;
    text-transform: uppercase; padding: 0.26rem 0.75rem;
    border-radius: 20px; margin-bottom: 0.7rem;
}
.page-title { font-size: 2rem; font-weight: 800; color: #fff; margin: 0 0 0.4rem 0; letter-spacing: -0.5px; }
.page-sub { color: #90b8e8; font-size: 0.95rem; margin: 0; line-height: 1.6; max-width: 600px; }
.section-title {
    font-size: 1.12rem; font-weight: 700; color: #e2f0ff;
    margin: 1.8rem 0 0.9rem 0; display: flex; align-items: center; gap: 0.5rem;
}
.section-title::after {
    content: ""; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(100,160,255,0.28), transparent);
    margin-left: 0.4rem;
}
div[data-testid="stMetric"] {
    background: rgba(18,48,88,0.55) !important;
    border: 1px solid rgba(100,160,255,0.18) !important;
    border-radius: 18px !important; padding: 1.15rem 1rem !important;
    backdrop-filter: blur(6px); transition: transform 0.2s ease, border-color 0.2s ease;
}
div[data-testid="stMetric"]:hover { transform: translateY(-3px); border-color: rgba(100,160,255,0.42) !important; }
div[data-testid="stMetric"] label { color: #90b8e8 !important; font-size: 0.78rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #fff !important; font-size: 1.75rem !important; font-weight: 700 !important; font-family: 'Space Mono', monospace !important; }
.pred-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 0.7rem; margin-top: 0.5rem; }
.pred-card {
    background: rgba(18,48,88,0.5); border: 1px solid rgba(100,160,255,0.15);
    border-radius: 18px; padding: 1.1rem 0.7rem; text-align: center;
    backdrop-filter: blur(6px); transition: transform 0.2s ease, background 0.2s ease;
}
.pred-card:hover { transform: translateY(-4px); background: rgba(28,68,128,0.65); border-color: rgba(100,160,255,0.38); }
.pred-day { font-size: 0.73rem; font-weight: 700; color: #7ec8ff; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.45rem; }
.pred-temp { font-size: 1.5rem; font-weight: 800; color: #fff; font-family: 'Space Mono', monospace; margin: 0.3rem 0; }
.pred-unit { font-size: 0.75rem; color: #90b8e8; font-weight: 600; }
.pred-label { font-size: 0.7rem; color: #506078; margin-top: 0.3rem; }
.info-card {
    background: rgba(18,48,88,0.45); border: 1px solid rgba(100,160,255,0.15);
    border-left: 3px solid #3898ff; border-radius: 12px;
    padding: 1rem 1.2rem; color: #90b8e8; font-size: 0.88rem;
    margin-bottom: 0.8rem; line-height: 1.6;
}
.corr-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.2rem; }
.corr-card {
    background: rgba(18,48,88,0.5); border: 1px solid rgba(100,160,255,0.18);
    border-radius: 18px; padding: 1.4rem 1rem; text-align: center;
    backdrop-filter: blur(6px); transition: transform 0.2s ease;
}
.corr-card:hover { transform: translateY(-3px); border-color: rgba(100,160,255,0.38); }
.corr-label { font-size: 0.78rem; color: #90b8e8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem; }
.corr-value { font-size: 2.2rem; font-weight: 800; color: #fff; font-family: 'Space Mono', monospace; }
.corr-sub { font-size: 0.72rem; color: #506078; margin-top: 0.3rem; }
.footer-bar { text-align:center; color:#2a4060; font-size:0.8rem; margin-top:2.5rem; padding-top:1rem; border-top:1px solid rgba(100,160,255,0.09); }
div[data-testid="stExpander"] { background: rgba(18,48,88,0.4) !important; border: 1px solid rgba(100,160,255,0.15) !important; border-radius: 14px !important; }
div[data-testid="stExpander"] summary { color: #90b8e8 !important; font-weight: 600 !important; }
[data-testid="stSlider"] label { color: #90b8e8 !important; font-weight: 600 !important; font-size: 0.9rem !important; }
@media (max-width: 640px) {
    .page-title { font-size: 1.5rem; }
    .pred-grid { grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); }
    .corr-row { grid-template-columns: 1fr; }
    .corr-value { font-size: 1.7rem; }
}
/* ---- Header Streamlit (area putih kanan atas) ---- */
header[data-testid="stHeader"] {
    background: rgba(13, 27, 42, 0.95) !important;
    backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(100,160,255,0.08);
}
header[data-testid="stHeader"]::before { background: transparent !important; }
header[data-testid="stHeader"] button,
header[data-testid="stHeader"] a { color: #90b8e8 !important; }
header[data-testid="stHeader"] svg { fill: #90b8e8 !important; }
[data-testid="stDecoration"] { display: none !important; }
</style>
'''
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
    df_bmkg_k = df_bmkg[["tanggal", "TAVG", "RR"]].copy()
    df_open_k = df_open[["tanggal", "TAVG_openmeteo", "precipitation_sum"]].copy()
    df = pd.merge(df_bmkg_k, df_open_k, on="tanggal", how="inner")
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
    f'<div class="info-card"> '
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
    f'<div class="corr-sub" style="margin-top:0.4rem;color:#7ec8ff;font-weight:600;">{corr_label(corr_temp)}</div>'
    '</div>'
    '<div class="corr-card">'
    '<div class="corr-label">🌧️ Korelasi Curah Hujan</div>'
    f'<div class="corr-value">{corr_rain:.3f}</div>'
    '<div class="corr-sub">BMKG RR vs Open-Meteo precipitation</div>'
    f'<div class="corr-sub" style="margin-top:0.4rem;color:#7ec8ff;font-weight:600;">{corr_label(corr_rain)}</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

# Statistik tambahan
col1, col2, col3, col4 = st.columns(4)
col1.metric('Rata-rata Suhu BMKG',        f'{df_compare["TAVG"].mean():.1f} °C')
col2.metric('Rata-rata Suhu Open-Meteo',   f'{df_compare["TAVG_openmeteo"].mean():.1f} °C')
col3.metric('Rata-rata Hujan BMKG',        f'{df_compare["RR"].mean():.1f} mm')
col4.metric('Rata-rata Hujan Open-Meteo',  f'{df_compare["precipitation_sum"].mean():.1f} mm')

# =========================
# GRAFIK SUHU
# =========================
st.markdown('<div class="section-title">🌡️ Perbandingan Suhu Rata-rata Harian</div>', unsafe_allow_html=True)
chart_suhu = (
    df_compare[["tanggal", "TAVG", "TAVG_openmeteo"]]
    .copy()
    .set_index("tanggal")
    .rename(columns={"TAVG": "BMKG", "TAVG_openmeteo": "Open-Meteo"})
)
st.line_chart(chart_suhu, color=["#ff8c00", "#3898ff"])

# =========================
# GRAFIK HUJAN
# =========================
st.markdown('<div class="section-title">🌧️ Perbandingan Curah Hujan Harian</div>', unsafe_allow_html=True)
chart_hujan = (
    df_compare[["tanggal", "RR", "precipitation_sum"]]
    .copy()
    .set_index("tanggal")
    .rename(columns={"RR": "BMKG", "precipitation_sum": "Open-Meteo"})
)
st.line_chart(chart_hujan, color=["#ff8c00", "#3898ff"])

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
