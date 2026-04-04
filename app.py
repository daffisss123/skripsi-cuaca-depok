import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import requests
import streamlit as st
from tensorflow.keras.models import load_model

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="Prediksi Cuaca Kota Depok",
    page_icon="🌤️",
    layout="wide",
)

# =========================
# KONSTANTA
# =========================
LAT_DEPOK = -6.4025
LON_DEPOK = 106.7942
CACHE_FILE = Path("data/processed/live_weather_cache.json")

FITUR = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "windspeed_10m_max",
    "relative_humidity_2m_max",
]

# =========================
# BANTUAN LABEL CUACA
# =========================
def weather_label(code: int) -> str:
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
        99: "Badai + Es Lebat",
    }
    return mapping.get(int(code), f"Kode {code}")

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

# =========================
# AMBIL DATA LIVE DENGAN FALLBACK
# =========================
@st.cache_data(ttl=3600)
def get_live_weather_depok():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT_DEPOK,
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
        "forecast_days": 7,
        "timezone": "Asia/Jakarta",
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

        return data, "live"

    except requests.exceptions.RequestException:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data, "cache"

        return None, "error"

# =========================
# UI HEADER
# =========================
st.title("🌤️ Prediksi Cuaca Kota Depok")
st.caption("Cuaca live Depok + forecast 7 hari + prediksi suhu maksimum berbasis model LSTM")

model, scaler = load_artifacts()
df_hist = load_hist_data()
live_data, live_source = get_live_weather_depok()

# =========================
# STATUS DATA LIVE
# =========================
if live_source == "cache":
    st.info("API live sedang dibatasi, jadi aplikasi memakai cache data terakhir yang berhasil diambil.")
elif live_source == "error":
    st.warning("Data live sementara tidak tersedia. Bagian prediksi model tetap bisa digunakan.")

# =========================
# CUACA SAAT INI
# =========================
st.subheader("Cuaca Saat Ini di Depok")

if live_data is not None:
    current = live_data["current"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Suhu Saat Ini", f'{current["temperature_2m"]:.1f} °C')
    c2.metric("Kelembaban", f'{current["relative_humidity_2m"]:.0f} %')
    c3.metric("Curah Hujan", f'{current["precipitation"]:.1f} mm')
    c4.metric("Kecepatan Angin", f'{current["wind_speed_10m"]:.1f} km/jam')

    st.write("**Kondisi sekarang:**", weather_label(current["weather_code"]))
else:
    st.write("Data live tidak tersedia saat ini.")

# =========================
# FORECAST 7 HARI
# =========================
st.subheader("Forecast 7 Hari ke Depan")

if live_data is not None:
    daily = live_data["daily"]
    df_daily = pd.DataFrame({
        "Tanggal": pd.to_datetime(daily["time"]).date,
        "Kondisi": [weather_label(x) for x in daily["weather_code"]],
        "Suhu Min (°C)": daily["temperature_2m_min"],
        "Suhu Maks (°C)": daily["temperature_2m_max"],
        "Curah Hujan (mm)": daily["precipitation_sum"],
        "Angin Maks (km/jam)": daily["wind_speed_10m_max"],
    })

    st.dataframe(df_daily, use_container_width=True, hide_index=True)
else:
    st.write("Forecast live tidak tersedia saat ini.")

# =========================
# PREDIKSI MODEL LSTM
# =========================
st.subheader("Prediksi Model LSTM")
st.caption("Bagian ini adalah hasil model penelitian untuk memprediksi suhu maksimum beberapa hari ke depan.")

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
    "Tanggal": tanggal_pred.date,
    "Prediksi Suhu Maksimum (°C)": np.round(hasil_prediksi_asli, 2),
})

st.dataframe(df_pred, use_container_width=True, hide_index=True)

# =========================
# RINGKASAN
# =========================
with st.expander("Lihat ringkasan data model"):
    st.write("Data historis model berakhir pada:", df_hist["tanggal"].max().date())
    st.write("Jumlah data historis model:", len(df_hist))
    st.write("Fitur model:", FITUR)

st.caption(f"Lokasi aplikasi: Kota Depok (lat {LAT_DEPOK}, lon {LON_DEPOK})")
