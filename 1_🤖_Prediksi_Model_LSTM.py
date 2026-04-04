import joblib
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
# KARTU HASIL PREDIKSI — RESPONSIF (CSS Grid auto-fill)
# =========================
st.markdown('<div class="section-title">🌡️ Hasil Prediksi Suhu Maksimum</div>', unsafe_allow_html=True)

cards_html = '<div class="pred-grid">'
for _, row in df_pred.iterrows():
    hari = row['Tanggal'].strftime('%a')
    tgl  = row['Tanggal'].strftime('%d %b')
    suhu = row['Prediksi Suhu Maksimum (°C)']
    if suhu >= 35:     warna = '#ff4444'
    elif suhu >= 33:   warna = '#ff8c00'
    elif suhu >= 30:   warna = '#ffd700'
    else:              warna = '#7ec8ff'
    cards_html += (
        '<div class="pred-card">'
        f'<div class="pred-day">{hari}<br>'
        f'<span style="font-weight:400;color:#304860;font-size:0.67rem">{tgl}</span></div>'
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
col3.metric('⚖️ Rata-rata', f'{hasil_asli.mean():.1f} °C')

# =========================
# GRAFIK HISTORIS
# =========================
st.markdown('<div class="section-title">📈 Riwayat Suhu Maks (120 Hari Terakhir)</div>', unsafe_allow_html=True)
chart_hist = (
    df_hist[["tanggal", "temperature_2m_max"]]
    .copy()
    .set_index("tanggal")
    .tail(120)
    .rename(columns={"temperature_2m_max": "Suhu Maks (°C)"})
)
st.line_chart(chart_hist, color=["#3898ff"])

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
