mport joblib
import numpy as np
import pandas as pd
import streamlit as st
from tensorflow.keras.models import load_model

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="Prediksi Model LSTM",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# STYLE  (sama persis dengan app.py — salin blok STYLE dari app.py ke sini)
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
.pred-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 0.65rem; margin-top: 0.5rem; }
.pred-card {
    background: #ffffff; border: 1px solid #c8ddf0; border-radius: 16px;
    padding: 1.1rem 0.6rem; text-align: center;
    box-shadow: 0 2px 8px rgba(30,80,160,0.07);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.pred-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(26,107,196,0.14); border-color: #91c0f0; }
.pred-day { font-size: 0.72rem; font-weight: 700; color: #1a6bc4; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.4rem; }
.pred-temp { font-size: 1.45rem; font-weight: 800; font-family: 'Space Mono', monospace; margin: 0.25rem 0; }
.pred-unit { font-size: 0.74rem; color: #5580a8; font-weight: 600; }
.pred-label { font-size: 0.68rem; color: #9ab8d8; margin-top: 0.25rem; }
div[data-testid="stExpander"] { background: #ffffff !important; border: 1px solid #c8ddf0 !important; border-radius: 14px !important; box-shadow: 0 2px 8px rgba(30,80,160,0.05); }
div[data-testid="stExpander"] summary { color: #1a3a5c !important; font-weight: 600 !important; }
[data-testid="stSlider"] label { color: #1a3a5c !important; font-weight: 600 !important; font-size: 0.9rem !important; }
.footer-bar { text-align:center; color:#8aabcc; font-size:0.8rem; margin-top:2.5rem; padding-top:1rem; border-top:1px solid #c8ddf0; }
@media (max-width: 560px) { .page-title { font-size: 1.5rem; } .pred-grid { grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); } }
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

# =========================
# KONSTANTA
# =========================
FITUR = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "windspeed_10m_max",
    "relative_humidity_2m_max",
]

# =========================
# LOAD MODEL & DATA
# =========================
@st.cache_resource
def load_artifacts():
    model  = load_model("model/model_final.keras")
    scaler = joblib.load("model/scaler.pkl")
    return model, scaler

@st.cache_data
def load_hist_data():
    df = pd.read_csv("data/processed/openmeteo_2019_2023_bersih.csv")
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df.sort_values("tanggal").reset_index(drop=True)

model, scaler = load_artifacts()
df_hist       = load_hist_data()

# =========================
# HEADER
# =========================
st.markdown("""
<div class="page-header">
    <div class="page-badge">🤖 Model LSTM &middot; Deep Learning</div>
    <h1 class="page-title">Prediksi Suhu Maksimum</h1>
    <p class="page-sub">
        Model LSTM dilatih menggunakan data historis Open-Meteo 2019&ndash;2023
        untuk memprediksi suhu maksimum harian Kota Depok hingga 7 hari ke depan.
    </p>
</div>
""", unsafe_allow_html=True)

# =========================
# INFO CARD
# =========================
st.markdown("""
<div class="info-card">
    📊 Model menggunakan <b>30 hari terakhir</b> sebagai input sequence
    untuk menghasilkan prediksi autoregresif ke depan.
    Setiap hari berikutnya menggunakan hasil prediksi sebelumnya sebagai input tambahan.
</div>
""", unsafe_allow_html=True)

# =========================
# SLIDER
# =========================
st.markdown('<div class="section-title">⚙️ Konfigurasi Prediksi</div>', unsafe_allow_html=True)
hari_prediksi = st.slider("Jumlah hari prediksi ke depan", min_value=1, max_value=7, value=3, step=1)

# =========================
# JALANKAN PREDIKSI
# =========================
data_scaled = scaler.transform(df_hist[FITUR].values)
input_seq   = data_scaled[-30:].copy()

hasil_scaled = []
for _ in range(hari_prediksi):
    pred = model.predict(input_seq[np.newaxis, :, :], verbose=0)[0][0]
    hasil_scaled.append(pred)
    baris_baru    = input_seq[-1].copy()
    baris_baru[0] = pred
    input_seq     = np.vstack([input_seq[1:], baris_baru])

dummy       = np.zeros((len(hasil_scaled), len(FITUR)))
dummy[:, 0] = hasil_scaled
hasil_asli  = scaler.inverse_transform(dummy)[:, 0]

tanggal_pred = pd.date_range(
    start=pd.Timestamp.now().normalize() + pd.Timedelta(days=1),
    periods=hari_prediksi,
)
df_pred = pd.DataFrame({
    "Tanggal":                     tanggal_pred,
    "Prediksi Suhu Maksimum (°C)": np.round(hasil_asli, 2),
})

# =========================
# KARTU HASIL PREDIKSI
# =========================
st.markdown('<div class="section-title">🌡️ Hasil Prediksi Suhu Maksimum</div>', unsafe_allow_html=True)

cards_html = '<div class="pred-grid">'
for _, row in df_pred.iterrows():
    hari = row['Tanggal'].strftime('%a')
    tgl  = row['Tanggal'].strftime('%d %b')
    suhu = row['Prediksi Suhu Maksimum (°C)']
    if suhu >= 35:   warna = '#c82020'
    elif suhu >= 33: warna = '#c86000'
    elif suhu >= 30: warna = '#a08000'
    else:            warna = '#1a6bc4'
    cards_html += (
        '<div class="pred-card">'
        f'<div class="pred-day">{hari}<br>'
        f'<span style="font-weight:400;color:#9ab8d8;font-size:0.66rem">{tgl}</span></div>'
        f'<div class="pred-temp" style="color:{warna};">{suhu:.1f}</div>'
        '<div class="pred-unit">°C</div>'
        '<div class="pred-label">Prediksi LSTM</div>'
        '</div>'
    )
cards_html += '</div>'
st.markdown(cards_html, unsafe_allow_html=True)

# =========================
# STATISTIK RINGKAS
# =========================
st.markdown('<div class="section-title">📊 Statistik Prediksi</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric('🔥 Suhu Tertinggi', f'{hasil_asli.max():.1f} °C')
col2.metric('❄️ Suhu Terendah', f'{hasil_asli.min():.1f} °C')
col3.metric('⚖️ Rata-rata',     f'{hasil_asli.mean():.1f} °C')

# =========================
# GRAFIK HISTORIS
# =========================
st.markdown('<div class="section-title">📈 Riwayat Suhu Maks (120 Hari Terakhir)</div>', unsafe_allow_html=True)
chart_hist = (
    df_hist[["tanggal", "temperature_2m_max"]]
    .copy().set_index("tanggal").tail(120)
    .rename(columns={"temperature_2m_max": "Suhu Maks (°C)"})
)
st.line_chart(chart_hist, color=["#1a6bc4"])

# =========================
# EXPANDER INFO MODEL
# =========================
with st.expander("ℹ️ Detail model & fitur yang digunakan"):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Informasi Data**")
        st.write("📅 Data berakhir pada:", df_hist["tanggal"].max().date())
        st.write("🔢 Jumlah data:", f"{len(df_hist):,} hari")
        st.write("🔁 Input sequence:", "30 hari terakhir")
    with c2:
        st.markdown("**Fitur Input Model**")
        for f in FITUR:
            st.markdown(f"- `{f}`")

st.markdown(
    '<div class="footer-bar">Model LSTM &middot; Skripsi Prediksi Cuaca Kota Depok</div>',
    unsafe_allow_html=True,
)
