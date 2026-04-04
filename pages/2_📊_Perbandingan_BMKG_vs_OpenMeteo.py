import pandas as pd
import streamlit as st

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="Perbandingan BMKG vs Open-Meteo",
    page_icon="📊",
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

    df_bmkg_kecil = df_bmkg[["tanggal", "TAVG", "RR"]].copy()
    df_open_kecil = df_open[["tanggal", "TAVG_openmeteo", "precipitation_sum"]].copy()

    df_compare = pd.merge(df_bmkg_kecil, df_open_kecil, on="tanggal", how="inner")
    return df_compare.sort_values("tanggal").reset_index(drop=True)

df_compare = load_compare_data()

# =========================
# HEADER
# =========================
st.markdown('<div class="section-title">📊 Perbandingan BMKG vs Open-Meteo</div>', unsafe_allow_html=True)
st.markdown(
    "<p class='small-note'>Bagian ini menunjukkan konsistensi pola data BMKG dengan Open-Meteo "
    "pada periode overlap (2024–2026).</p>",
    unsafe_allow_html=True
)

# =========================
# METRIK KORELASI
# =========================
col_a, col_b = st.columns(2)
with col_a:
    corr_temp = df_compare["TAVG"].corr(df_compare["TAVG_openmeteo"])
    st.metric("Korelasi Suhu (BMKG vs Open-Meteo)", f"{corr_temp:.3f}")
with col_b:
    corr_rain = df_compare["RR"].corr(df_compare["precipitation_sum"])
    st.metric("Korelasi Curah Hujan (BMKG vs Open-Meteo)", f"{corr_rain:.3f}")

# =========================
# GRAFIK SUHU
# =========================
st.markdown("**Perbandingan Suhu Rata-Rata Harian**")
chart_suhu = df_compare[["tanggal", "TAVG", "TAVG_openmeteo"]].copy().set_index("tanggal")
st.line_chart(chart_suhu)

# =========================
# GRAFIK CURAH HUJAN
# =========================
st.markdown("**Perbandingan Curah Hujan Harian**")
chart_hujan = df_compare[["tanggal", "RR", "precipitation_sum"]].copy().set_index("tanggal")
st.line_chart(chart_hujan)

# =========================
# TABEL DATA TERBARU
# =========================
with st.expander("📋 Lihat data perbandingan terbaru"):
    st.dataframe(df_compare.tail(20), use_container_width=True, hide_index=True)
