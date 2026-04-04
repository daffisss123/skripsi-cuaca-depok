import json
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
    layout="wide"
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
    "relative_humidity_2m_max"
]

# =========================
# STYLE
# =========================
st.markdown("""
<style>
    .hero {
        padding: 1.3rem 1.4rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #eef6ff 0%, #f8fbff 100%);
        border: 1px solid #dbeafe;
        margin-bottom: 1rem;
    }
    .hero h1 {
        margin: 0;
        color: #0f172a;
        font-size: 2.3rem;
    }
    .hero p {
        color: #334155;
        margin-top: 0.5rem;
        margin-bottom: 0;
        font-size: 1rem;
    }
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
    .footer-note {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 1rem;
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
# LABEL CUACA UNTUK KONTEKS DEPOK
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
        99: "Badai Petir"
    }
    return mapping.get(int(code), "Cuaca Tidak Diketahui")

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

    df_bmkg_kecil = df_bmkg[["tanggal", "TAVG", "RR"]].copy()
    df_open_kecil = df_open[["tanggal", "TAVG_openmeteo", "precipitation_sum"]].copy()

    df_compare = pd.merge(df_bmkg_kecil, df_open_kecil, on="tanggal", how="inner")
    return df_compare.sort_values("tanggal").reset_index(drop=True)

# =========================
# DATA LIVE DENGAN FALLBACK CACHE
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
# LOAD SEMUA
# =========================
model, scaler = load_artifacts()
df_hist = load_hist_data()
df_compare = load_compare_data()
live_data, live_source = get_live_weather_depok()

# =========================
# HERO
# =========================
st.markdown("""
<div class="hero">
    <h1>🌤️ Prediksi Cuaca Kota Depok</h1>
    <p>
        Aplikasi ini menampilkan cuaca live di Depok, forecast 7 hari ke depan,
        prediksi suhu maksimum berbasis model LSTM, dan perbandingan data BMKG dengan Open-Meteo.
    </p>
</div>
""", unsafe_allow_html=True)

if live_source == "cache":
    st.info("API live sedang dibatasi, jadi aplikasi menggunakan cache data terakhir yang berhasil diambil.")
elif live_source == "error":
    st.warning("Data live sementara tidak tersedia. Bagian prediksi model dan perbandingan data tetap bisa digunakan.")

# =========================
# TAB UTAMA
# =========================
tab1, tab2, tab3 = st.tabs([
    "Cuaca Live Depok",
    "Prediksi Model LSTM",
    "Perbandingan BMKG vs Open-Meteo"
])

# =========================
# TAB 1: CUACA LIVE
# =========================
with tab1:
    st.markdown('<div class="section-title">Cuaca Saat Ini di Depok</div>', unsafe_allow_html=True)

    if live_data is not None:
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
                st.markdown(
                    f"""
                    <div class="forecast-card">
                        <div class="forecast-day">{row['tanggal'].strftime('%a, %d %b')}</div>
                        <div class="forecast-main">{weather_label(int(row['weather_code']))}</div>
                        <div class="forecast-sub">🌡️ {row['temp_min']:.1f}° - {row['temp_max']:.1f}°</div>
                        <div class="forecast-sub">🌧️ {row['hujan']:.1f} mm</div>
                        <div class="forecast-sub">💨 {row['angin_max']:.1f} km/jam</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.write("Data cuaca live tidak tersedia saat ini.")

# =========================
# TAB 2: PREDIKSI MODEL
# =========================
with tab2:
    st.markdown('<div class="section-title">Prediksi Model LSTM</div>', unsafe_allow_html=True)
    st.markdown(
        "<p class='small-note'>Model penelitian ini memprediksi suhu maksimum beberapa hari ke depan berdasarkan histori data Open-Meteo.</p>",
        unsafe_allow_html=True
    )

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

    st.markdown('<div class="section-title">Riwayat Suhu Maksimum</div>', unsafe_allow_html=True)
    chart_hist = df_hist[["tanggal", "temperature_2m_max"]].copy().set_index("tanggal").tail(120)
    st.line_chart(chart_hist)

    with st.expander("Lihat ringkasan data model"):
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

# =========================
# TAB 3: PERBANDINGAN DATA
# =========================
with tab3:
    st.markdown('<div class="section-title">Perbandingan BMKG vs Open-Meteo</div>', unsafe_allow_html=True)
    st.markdown(
        "<p class='small-note'>Bagian ini menunjukkan konsistensi pola data BMKG dengan Open-Meteo pada periode overlap.</p>",
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns(2)
    with col_a:
        corr_temp = df_compare["TAVG"].corr(df_compare["TAVG_openmeteo"])
        st.metric("Korelasi Suhu", f"{corr_temp:.3f}")
    with col_b:
        corr_rain = df_compare["RR"].corr(df_compare["precipitation_sum"])
        st.metric("Korelasi Curah Hujan", f"{corr_rain:.3f}")

    st.markdown("**Perbandingan Suhu**")
    chart_suhu = df_compare[["tanggal", "TAVG", "TAVG_openmeteo"]].copy().set_index("tanggal")
    st.line_chart(chart_suhu)

    st.markdown("**Perbandingan Curah Hujan**")
    chart_hujan = df_compare[["tanggal", "RR", "precipitation_sum"]].copy().set_index("tanggal")
    st.line_chart(chart_hujan)

    with st.expander("Lihat data perbandingan terbaru"):
        st.dataframe(df_compare.tail(20), use_container_width=True, hide_index=True)

st.markdown(
    f"<p class='footer-note'>Lokasi aplikasi: Kota Depok (lat {LAT_DEPOK}, lon {LON_DEPOK})</p>",
    unsafe_allow_html=True
)
