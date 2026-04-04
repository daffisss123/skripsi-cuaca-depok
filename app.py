
import streamlit as st
import pandas as pd
import numpy as np
import requests
import joblib
from tensorflow.keras.models import load_model

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
  page_title="Prediksi Cuaca Kota Depok",
  page_icon="🌤️",
  layout="wide"
)

# =========================
# CSS SEDERHANA AGAR LEBIH MENARIK
# =========================
st.markdown("""
<style>
    .hero {
      padding: 1.2rem 1.2rem 0.8rem 1.2rem;
      border-radius: 18px;
      background: linear-gradient(135deg, #eef6ff 0%, #f8fbff 100%);
      border: 1px solid #dbeafe;
      margin-bottom: 1rem;
    }
    .hero h1 {
      margin: 0;
      color: #0f172a;
      font-size: 2.2rem;
    }
    .hero p {
      color: #334155;
      margin-top: 0.45rem;
      margin-bottom: 0;
    }
    .section-tittle {
      margin-top: 1rem;
      margin-bottom: 0.6rem;
      color: #0f172a;
      font-weight: 700;
      font-size: 1.35rem;
    }
    .small-note {
      color: #475569;
      font-size: 0.95rem;
    }
    .forecast-card { 
      padding: 0.9rem;
      border-radius: 14px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      text-align: center;
      box-shadow: 0 1px 4px rgba(0,0,0,0.05);
      margin-bottom: 0.6rem;
    }
    .forecast-day {
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 0.35rem;
      font-size: 0.95rem;
    }
    .forecast-main { 
      font-size: 1.05rem;
      color: #1d4ed8;
      font-weight: 700;
      margin-bottom: 0.25rem;
    }
    .forecast-sub { 
      color: #475569;
      font-size: 0.9rem;
      margin-bottom: 0.15rem;
    }
    .footer-note {
      font-size: 0.9rem;
      color: #475569;
      margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# FUNGSI BANTU
# =========================
def weather_label(code):
  mapping = {
    0: "Cerah",
    1: "Cerah Berawan",
    2: "Berawan",
    3: "Mendung",
    45: "Kabut",
    48: "Kabut Tebal",
    51: "Gerimis Ringan",
    53: "Gerimis",
    55: "Gerimis Lebat",
    61: "Hujan Ringan",
    63: "Hujan",
    65: "Hujan Lebat",
    66: "Hujan Beku Ringan",
    67: "Hujan Beku Lebat",
    71: "Salju Ringan",
    73: "Salju",
    75: "Salju Lebat",
    77: "Butiran Es",
    80: "Hujan Lokal Ringan",
    81: "Hujan Lokal",
    82: "Hujan Lokal Lebat",
    85: "Salju Lokal Ringan",
    86: "Salju Lokal Lebat",
    95: "Badai Petir",
    96: "Badai + Es Ringan",
    99: "Badai + Es Lebat"
  }
  return mapping.get(code, f"kode {code}")

# =========================
# LOAD ARTIFACT MODEL
# =========================
@st.cache_resource
def load_artifacts():
  model = load_model("model/model_final.keras")
  scaler = joblib.load("model/scaler.pkl")
  return model, scaler

# =========================
# LOAD DATA HISTORIS MODEL
# =========================
@st.cache_data
def load_hist_data():
  df = pd.read_csv("data/processed/openmeteo_2019_2023_bersih.csv")
  df["tanggal"] = pd.to_datetime(df["tanggal"])
  return df.sort_values("tanggal").reset_index(drop=True)

# =========================
# LOAD DATA LIVE DEPOK
# =========================
@st.cache_data(ttl=1800)
def get_live_weather_depok():
  url = "https://api.open-meteo.com/v1/forecast"
  params = {
    "latitude": -6.4025,
    "longitude": 106.7942,
    "current": [
      "temperature_2m",
      "relative_humidity_2m",
      "precipitation",
      "wind_speed_10m",
      "weather_code"
    ],
    "daily": [
      "weather_code",
      "temperature_2m_max",
      "temperature_2m_min",
      "precipitation_sum",
      "wind_speed_10m_max"
    ],
    "forecast_days": 7,
    "timezone": "Asia/Jakarta"
  }
  response = requests.get(url, params=params, timeout=30)
  response.raise_for_status()
  return response.json()

# =========================
# LOAD SEMUA YANG DIPERLUKAN
# =========================
model, scaler = load_artifacts()
df_hist = load_hist_data()
live_data = get_live_weather_depok()

# =========================
# HERO
# =========================
st.markdown("""
<div class="hero">
    <h1>🌤️ Prediksi Cuaca Kota Depok</h1>
    <p>
         Aplikasi ini menampilkan cuaca live untuk Depok, forecast 7 hari ke depan,
         dan prediksi suhu maksimum berbasis model LSTM.
    <p>
</div>
""", unsafe_allow_html=True)

# =========================
# DATA LIVE SEKARANG
# =========================
st.markdown('<div class="section-title">Cuaca Saat Ini di Depok</div>', unsafe_allow_html=True)

current = live_data["current"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Suhu Saat Ini", f'{current["temperature_2m"]:.1f} °C')
c2.metric("Kelembaban", f'{current["relative_humidity_2m"]:.0f} %')
c3.metric("Curah Hujan", f'{current["precipitation"]:.1f} mm')
c4.metric("Kecepatan Angin", f'{current["wind_speed_10m"]:.1f} km/jam')

st.markdown(
    f"<p class='small-note'><b>Kondisi sekarang:</b> {weather_label(current['weather_code'])}</p>",
    unsafe_allow_html=True
)

# =========================
# FORECAST 7 HARI
# =========================
st.markdown('<div class="section-title">Forecast 7 Hari ke Depan</div>', unsafe_allow_html=True)

daily = live_data["daily"]
df_daily = pd.DataFrame({
  "tanggal": pd.to_datetime(daily["time"]),
  "weather_code": daily["weather_code"],
  "temp_max": daily["temperature_2m_max"],
  "temp_min": daily["temperature_2m_min"],
  "hujan": daily["precipitation_sum"],
  "angin_max": daily["wind_speed_10m_max"]
})

cols = st.columns(7)
for i, row in df_daily.iterrows():
  with cols[i]:
    st.markdown(f"""
    <div class="forecast-card">
        <div class="forecast-day">{row['tanggal'].strftime('%a, %d %b')}</div>
        <div class="forecast-main">{weather_label(int(row['weather_code']))}</div>
        <div class="forecast-sub">🌡️ {row['temp_min']:.1f}° - {row['temp_max']:.1f}°</div>
        <div class="forecast-sub">🌧️ {row['hujan']:.1f} mm</div>
        <div class="forecast-sub">💨 {row['angin_max']:.1f} km/jam</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# PREDIKSI MODEL LSTM
# =========================
st.markdown('<div class="section-title">Prediksi Model LSTM</div>', unsafe_allow_html=True)
st.markdown(
  "<p class='small-note'>Bagian ini adalah hasil model penelitianmu untuk memprediksi suhu maksimum beberapa hari ke depan.</p>",
  unsafe_allow_html=True
)

fitur = [
  "temperature_2m_max",
  "temperature_2m_min",
  "precipitation_sum",
  "windspeed_10m_max",
  "relative_humidity_2m_max"
]

hari_prediksi = st.slider("Pilih jumlah hari prediksi model", 1, 7, 3)

data_scaled = scaler.transform(df_hist[fitur].values)
input_seq = data_scaled[-30:].copy()

hasil_prediksi_scaled = []

for _ in range(hari_prediksi):
  pred = model.predict(input_seq[np.newaxis, :, :], verbose=0)[0][0]
  hasil_prediksi_scaled.append(pred)

  baris_baru = input_seq[-1].copy()
  baris_baru[0] = pred
  input_seq = np.vstack([input_seq[1:], baris_baru])

dummy = np.zeros((len(hasil_prediksi_scaled), len(fitur)))
dummy[:, 0] = hasil_prediksi_scaled
hasil_prediksi_asli = scaler.inverse_transform(dummy)[:, 0]

tanggal_pred = pd.date_range(
  start=pd.Timestamp.now().normalize() + pd.Timedelta(days=1),
  periods=hari_prediksi
)

df_pred = pd.DataFrame({
  "Tanggal": tanggal_pred,
  "Prediksi Suhu Maksimum (°C)": hasil_prediksi_asli
})

pred_cols = st.columns(hari_prediksi)
for i, row in df_pred.iterrows():
  with pred_cols[i]:
    st.markdown(f"""
    <div class="forecast-card">
        <div class="forecast-day">{row['Tanggal'].strftime('%a, %d %b')}</div>
        <div class="forecast-main">{row['Prediksi Suhu Maksimum (°C)']:.2f} °C</div>
        <div class="forecast-sub">Prediksi model LSTM</div>
    </div>
    """, unsafe_allow_html=True)

with st.expander("Lihat ringkasan data model"):
   st.write("Data historis model berakhir pada:", df_hist["tanggal"].max().date())
   st.write("Jumlah data historis model:", len(df_hist))
   st.write("Fitur model:", fitur)

st.markdown(
  "<p class='footer-note'>Lokasi aplikasi: Kota Depok (lat -6.4025, lon 106.7942)</p>",
  unsafe_allow_html=True
)
