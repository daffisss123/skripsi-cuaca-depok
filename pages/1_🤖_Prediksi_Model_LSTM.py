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
    layout="wide"
)

# =========================
# STYLE
# =========================
st.markdown("""
<style>
    .section-title {
        margin-top: 0.4rem;
        margin-bottom: 0.7rem;
        color: #0f172a;
        font-weight: 700;
        font-size: 1.3rem;
    }
    .small-note {
        color: #475569;
        font-size: 0.95rem;
    }
    .forecast-card {
        padding: 0.9rem;
        border-radius: 16px;
        background: white;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .forecast-day {
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.35rem;
        font-size: 0.95rem;
    }
    .forecast-main {
        font-size: 1rem;
        color: #1d4ed8;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .forecast-sub {
        color: #475569;
        font-size: 0.9rem;
        margin-bottom: 0.12rem;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 0.8rem;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# KONSTANTA
# =========================
FITUR = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "windspeed_10m_max",
    "relative_humidity_2m_max"
]

# =========================
# LOAD MODEL & DATA
# =========================
@st.cache_resource
def load_artifacts():
    model = load_model("model/model_final.keras")
    scaler = joblib.load("model/scaler.pkl")
    return model, scaler

@st.cache_data
def load_hist_data():
    df = pd.read_csv("data/processed/openmeteo_2019_2023_bersih.csv")
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df.sort_values("tanggal").reset_index(drop=True)

model, scaler = load_artifacts()
df_hist = load_hist_data()

# =========================
# HEADER
# =========================
st.markdown('<div class="section-title">🤖 Prediksi Model LSTM</div>', unsafe_allow_html=True)
st.markdown(
    "<p class='small-note'>Model penelitian ini memprediksi suhu maksimum beberapa hari ke depan "
    "berdasarkan histori data Open-Meteo (2019–2023).</p>",
    unsafe_allow_html=True
)

# =========================
# SLIDER & PREDIKSI
# =========================
hari_prediksi = st.slider("Pilih jumlah hari prediksi model", 1, 7, 3)

data_scaled = scaler.transform(df_hist[FITUR].values)
input_seq = data_scaled[-30:].copy()

hasil_prediksi_scaled = []

for _ in range(hari_prediksi):
    pred = model.predict(input_seq[np.newaxis, :, :], verbose=0)[0][0]
    hasil_prediksi_scaled.append(pred)

    baris_baru = input_seq[-1].copy()
    baris_baru[0] = pred
    input_seq = np.vstack([input_seq[1:], baris_baru])

dummy = np.zeros((len(hasil_prediksi_scaled), len(FITUR)))
dummy[:, 0] = hasil_prediksi_scaled
hasil_prediksi_asli = scaler.inverse_transform(dummy)[:, 0]

tanggal_pred = pd.date_range(
    start=pd.Timestamp.now().normalize() + pd.Timedelta(days=1),
    periods=hari_prediksi
)

df_pred = pd.DataFrame({
    "Tanggal": tanggal_pred,
    "Prediksi Suhu Maksimum (°C)": np.round(hasil_prediksi_asli, 2)
})

# =========================
# KARTU HASIL PREDIKSI
# =========================
pred_cols = st.columns(hari_prediksi)
for i, row in df_pred.iterrows():
    with pred_cols[i]:
        st.markdown(
            f"""
            <div class="forecast-card">
                <div class="forecast-day">{row['Tanggal'].strftime('%a, %d %b')}</div>
                <div class="forecast-main">{row['Prediksi Suhu Maksimum (°C)']:.2f} °C</div>
                <div class="forecast-sub">Prediksi model LSTM</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================
# RIWAYAT SUHU HISTORIS
# =========================
st.markdown('<div class="section-title">Riwayat Suhu Maksimum (120 Hari Terakhir)</div>', unsafe_allow_html=True)
chart_hist = df_hist[["tanggal", "temperature_2m_max"]].copy().set_index("tanggal").tail(120)
st.line_chart(chart_hist)

# =========================
# RINGKASAN INFO MODEL
# =========================
with st.expander("ℹ️ Lihat ringkasan data model"):
    st.write("Data historis model berakhir pada:", df_hist["tanggal"].max().date())
    st.write("Jumlah data historis model:", len(df_hist))
    st.markdown("""
**Fitur yang digunakan model:**
- Suhu maksimum harian (`temperature_2m_max`)
- Suhu minimum harian (`temperature_2m_min`)
- Curah hujan harian (`precipitation_sum`)
- Kecepatan angin maksimum (`windspeed_10m_max`)
- Kelembaban maksimum (`relative_humidity_2m_max`)
""")
