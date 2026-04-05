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
# STYLE — Light Premium
# =========================
STYLE = '''
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Mono:wght@700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: linear-gradient(160deg, #f0f4ff 0%, #e8f0fe 50%, #f5f7ff 100%); min-height: 100vh; }
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.97) !important;
    border-right: 1px solid rgba(99,130,255,0.12);
    box-shadow: 2px 0 16px rgba(99,130,255,0.07);
}
.page-header {
    background: linear-gradient(135deg, #4f8ef7 0%, #2563eb 60%, #1d4ed8 100%);
    border-radius: 24px;
    padding: 1.8rem 2.2rem; margin-bottom: 1.8rem;
    position: relative; overflow: hidden;
    box-shadow: 0 8px 32px rgba(37,99,235,0.22);
}
.page-header::before {
    content: ""; position: absolute; top: -60px; right: -60px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
    border-radius: 50%; pointer-events: none;
}
.page-badge {
    display: inline-block; background: rgba(255,255,255,0.22);
    border: 1px solid rgba(255,255,255,0.38); color: #fff;
    font-size: 0.73rem; font-weight: 600; letter-spacing: 0.09em;
    text-transform: uppercase; padding: 0.26rem 0.75rem;
    border-radius: 20px; margin-bottom: 0.7rem;
}
.page-title { font-size: 2rem; font-weight: 800; color: #fff; margin: 0 0 0.4rem 0; letter-spacing: -0.5px; }
.page-sub { color: rgba(255,255,255,0.82); font-size: 0.95rem; margin: 0; line-height: 1.6; max-width: 600px; }
.section-title {
    font-size: 1.08rem; font-weight: 700; color: #1e3a5f;
    margin: 1.8rem 0 0.9rem 0; display: flex; align-items: center; gap: 0.5rem;
}
.section-title::after {
    content: ""; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(37,99,235,0.2), transparent);
    margin-left: 0.4rem;
}
div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid rgba(99,130,255,0.15) !important;
    border-radius: 18px !important; padding: 1.15rem 1rem !important;
    box-shadow: 0 2px 12px rgba(37,99,235,0.07);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(37,99,235,0.14) !important; }
div[data-testid="stMetric"] label { color: #5b7ba8 !important; font-size: 0.78rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #1e3a5f !important; font-size: 1.75rem !important; font-weight: 700 !important; font-family: 'Space Mono', monospace !important; }
.pred-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 0.7rem; margin-top: 0.5rem; }
.pred-card {
    background: #ffffff; border: 1px solid rgba(99,130,255,0.13);
    border-radius: 18px; padding: 1.1rem 0.7rem; text-align: center;
    box-shadow: 0 2px 10px rgba(37,99,235,0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.pred-card:hover { transform: translateY(-4px); box-shadow: 0 10px 28px rgba(37,99,235,0.13); border-color: rgba(37,99,235,0.22); }
.pred-day { font-size: 0.73rem; font-weight: 700; color: #2563eb; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.45rem; }
.pred-temp { font-size: 1.5rem; font-weight: 800; color: #1e3a5f; font-family: 'Space Mono', monospace; margin: 0.3rem 0; }
.pred-unit { font-size: 0.75rem; color: #5b7ba8; font-weight: 600; }
.pred-label { font-size: 0.7rem; color: #94a3b8; margin-top: 0.3rem; }
.info-card {
    background: #eff6ff; border: 1px solid #bfdbfe;
    border-left: 3px solid #2563eb; border-radius: 12px;
    padding: 1rem 1.2rem; color: #1e40af; font-size: 0.88rem;
    margin-bottom: 0.8rem; line-height: 1.6;
}
.corr-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.2rem; }
.corr-card {
    background: #ffffff; border: 1px solid rgba(99,130,255,0.15);
    border-radius: 18px; padding: 1.4rem 1rem; text-align: center;
    box-shadow: 0 2px 10px rgba(37,99,235,0.06);
    transition: transform 0.2s ease;
}
.corr-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(37,99,235,0.12); }
.corr-label { font-size: 0.78rem; color: #5b7ba8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem; }
.corr-value { font-size: 2.2rem; font-weight: 800; color: #1e3a5f; font-family: 'Space Mono', monospace; }
.corr-sub { font-size: 0.72rem; color: #94a3b8; margin-top: 0.3rem; }
.footer-bar { text-align:center; color:#94a3b8; font-size:0.8rem; margin-top:2.5rem; padding-top:1rem; border-top:1px solid rgba(99,130,255,0.12); }
div[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid rgba(99,130,255,0.13) !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.05);
}
div[data-testid="stExpander"] summary { color: #2563eb !important; font-weight: 600 !important; }
[data-testid="stSlider"] label { color: #1e3a5f !important; font-weight: 600 !important; font-size: 0.9rem !important; }
@media (max-width: 640px) {
    .page-title { font-size: 1.5rem; }
    .pred-grid { grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); }
    .corr-row { grid-template-columns: 1fr; }
    .corr-value { font-size: 1.7rem; }
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
# KARTU HASIL PREDIKSI
# =========================
st.markdown('<div class="section-title">🌡️ Hasil Prediksi Suhu Maksimum</div>', unsafe_allow_html=True)

cards_html = '<div class="pred-grid">'
for _, row in df_pred.iterrows():
    hari = row['Tanggal'].strftime('%a')
    tgl  = row['Tanggal'].strftime('%d %b')
    suhu = row['Prediksi Suhu Maksimum (°C)']
    if suhu >= 35:     warna = '#ef4444'
    elif suhu >= 33:   warna = '#f97316'
    elif suhu >= 30:   warna = '#eab308'
    else:              warna = '#2563eb'
    cards_html += (
        '<div class="pred-card">'
        f'<div class="pred-day">{hari}<br>'
        f'<span style="font-weight:400;color:#94a3b8;font-size:0.67rem">{tgl}</span></div>'
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
st.line_chart(chart_hist, color=["#2563eb"])

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
