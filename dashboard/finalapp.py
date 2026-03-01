import time
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from supabase import create_client
import requests
from datetime import date


sns.set_theme(
    style="dark",
    rc={
        "axes.facecolor": "#0F172A",
        "figure.facecolor": "#0B0F14",
        "axes.edgecolor": "#E5E7EB",
        "axes.labelcolor": "#E5E7EB",
        "text.color": "#E5E7EB",
        "xtick.color": "#E5E7EB",
        "ytick.color": "#E5E7EB",
        "grid.color": "#1F2937"
    }
)

st.set_page_config(page_title="Smart Fan Energy Watch", layout="wide")
st.title("Smart Fan Energy Watch — Live")

# --- Secrets ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
sb = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- Sidebar controls ---
st.sidebar.header("Live settings")
REFRESH_SEC = st.sidebar.slider("Refresh interval (seconds)", 1, 10, 2)
DEVICE_ID = st.sidebar.text_input("device_id filter (optional)", value="esp32_01")
LIMIT = st.sidebar.slider("Rows to display", 50, 1000, 200)
st.sidebar.header("Savings assumptions")
BASELINE_W = st.sidebar.number_input("Baseline power (W) (e.g., HIGH mode)", min_value=0.0, value=2.949, step=0.1)
PRICE_PER_KWH = st.sidebar.number_input("Electricity price ($/kWh)", min_value=0.0, value=0.35, step=0.01)


# --- Helper: fetch latest rows ---
@st.cache_data(ttl=1)
def fetch_latest(limit: int, device_id: str | None):
    q = sb.table("fan_readings").select("created_at,temp_c,power_w,fan_mode,device_id").order("created_at", desc=True).limit(limit)
    if device_id:
        q = q.eq("device_id", device_id)
    data = q.execute().data
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True).dt.tz_convert("America/Los_Angeles")
    df = df.sort_values("created_at")
    return df


def energy_kwh_from_power(df: pd.DataFrame, time_col="created_at", power_col="power_w") -> float:
    d = df.copy().sort_values(time_col)
    dt_h = d[time_col].diff().dt.total_seconds() / 3600.0
    dt_h = dt_h.clip(lower=0).fillna(0)
    return float((d[power_col].astype(float) * dt_h).sum() / 1000.0)

def baseline_kwh_constant(df: pd.DataFrame, baseline_watts: float, time_col="created_at") -> float:
    d = df.copy().sort_values(time_col)
    dt_h = d[time_col].diff().dt.total_seconds() / 3600.0
    dt_h = dt_h.clip(lower=0).fillna(0)
    return float((baseline_watts * dt_h).sum() / 1000.0)

def format_duration(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}h {m}m {s}s"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"

@st.cache_data(ttl=1800)  # cache for 30 minutes
def get_weather_today(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "temperature_unit": "fahrenheit",
        "timezone": "America/Los_Angeles",
        "current": "temperature_2m",
        "daily": "temperature_2m_max",
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    j = r.json()

    cur = j.get("current", {}).get("temperature_2m", None)
    if cur is None:
        raise ValueError("Open-Meteo current temperature missing")
    current_f = float(cur)

    today_str = date.today().isoformat()
    days = j["daily"]["time"]
    peaks = j["daily"]["temperature_2m_max"]

    if today_str in days:
        i = days.index(today_str)
        peak_f = float(peaks[i])
    else:
        peak_f = float(peaks[0])

    return current_f, peak_f

def weather_thresholds(now_f: float, peak_f: float):
    med_at = float(now_f)
    high_at = float(peak_f) - 1.0
    if high_at < med_at + 2:
        high_at = med_at + 2
    return med_at, high_at

def c_to_f(c: float) -> float:
    return c * 9.0/5.0 + 32.0
# --- Live area placeholders (so the page doesn't jump) ---
top = st.empty()

# --- A simple "polling" loop ---
# Streamlit reruns top-to-bottom; we trigger reruns with sleep + st.rerun()
if "live" not in st.session_state:
    st.session_state.live = True

with top:
    st.caption("Live mode: polling Supabase and refreshing automatically.")

df = fetch_latest(LIMIT, DEVICE_ID.strip() if DEVICE_ID.strip() else None)

# --- Weather Location ---
LAT = 32.6859
LON = -117.1831

try:
    outdoor_now_f, outdoor_peak_f = get_weather_today(LAT, LON)
except Exception as e:
    st.sidebar.warning(f"Weather fetch failed: {e}")
    outdoor_now_f, outdoor_peak_f = None, None

if outdoor_now_f is not None and outdoor_peak_f is not None:
    med_threshold_f, high_threshold_f = weather_thresholds(outdoor_now_f, outdoor_peak_f)
else:
    med_threshold_f, high_threshold_f = None, None

if med_threshold_f is not None:
    st.sidebar.info(
        f"Weather now {outdoor_now_f:.0f}°F | peak {outdoor_peak_f:.0f}°F\n"
        f"→ MED ≥ {med_threshold_f:.0f}°F, HIGH ≥ {high_threshold_f:.0f}°F"
    )

if df.empty:
    st.warning("No rows found yet. Make sure ESP32 is inserting into `fan_readings` and device_id matches.")
else:
     # --- Metrics ---
    last = df.iloc[-1]
    indoor_f = c_to_f(float(last["temp_c"]))

    # Window stats
    window_seconds = (df["created_at"].iloc[-1] - df["created_at"].iloc[0]).total_seconds()
    avg_interval_seconds = df["created_at"].diff().dt.total_seconds().dropna().mean()
    avg_interval_seconds = float(avg_interval_seconds) if pd.notna(avg_interval_seconds) else 0.0

    # Energy + savings stats
    actual_kwh = energy_kwh_from_power(df)
    base_kwh = baseline_kwh_constant(df, float(BASELINE_W))
    saved_kwh = max(0.0, base_kwh - actual_kwh)
    pct_saved = (saved_kwh / base_kwh * 100.0) if base_kwh > 0 else 0.0

    # Cost stats
    cost_used = actual_kwh * float(PRICE_PER_KWH)
    cost_saved = saved_kwh * float(PRICE_PER_KWH)

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Time", last["created_at"].strftime("%H:%M:%S"))
    m2.metric("Temp °C", f"{float(last['temp_c']):.1f}")
    m3.metric("Power W", f"{float(last['power_w']):.2f}")
    m4.metric("Mode", str(last.get("fan_mode", "")))
    m5.metric("Used kWh", f"{actual_kwh:.4f}", delta=f"${cost_used:.2f}")
    m6.metric("Saved %", f"{pct_saved:.1f}%", delta=f"${cost_saved:.2f}")

    st.caption(f"Window: {format_duration(window_seconds)} • Avg interval: {avg_interval_seconds:.1f}s")

    st.caption(
        f"Baseline assumes constant {float(BASELINE_W):.3f} W over this same time window. "
        f"Estimated cost saved: ${cost_saved:.2f} (price = ${float(PRICE_PER_KWH):.2f}/kWh)."
    )

    # --- Table ---
    st.subheader("Latest readings")
    st.dataframe(df.tail(50), use_container_width=True)

    st.subheader("Mode breakdown (time-weighted)")
    # Time-weighted % in each mode using dt between readings
    d = df.copy().sort_values("created_at")
    d["dt_s"] = d["created_at"].diff().dt.total_seconds().fillna(0)

    # Use the previous mode for each interval (more correct), fallback to current if needed
    d["mode_for_interval"] = d["fan_mode"].shift(1).fillna(d["fan_mode"])

    mode_seconds = d.groupby("mode_for_interval")["dt_s"].sum().sort_values(ascending=False)
    total_seconds = mode_seconds.sum()

    if total_seconds > 0:
        mode_pct = (mode_seconds / total_seconds * 100.0).round(1)
        mode_table = pd.DataFrame({"seconds": mode_seconds.round(1), "percent": mode_pct})
        st.dataframe(mode_table, use_container_width=True)

        # Optional quick bar chart
        fig_mode = plt.figure(figsize=(6, 3))
        sns.barplot(x=mode_pct.index.astype(str), y=mode_pct.values)
        plt.xlabel("Fan mode")
        plt.ylabel("Percent of time (%)")
        plt.tight_layout()
        st.pyplot(fig_mode, clear_figure=True)
    else:
        st.info("Not enough time range yet to compute mode breakdown.")
    # --- Charts ---
    left, right = st.columns(2)

    with left:
        st.subheader("Temperature vs time")
        fig1 = plt.figure(figsize=(7, 4))
        sns.lineplot(data=df, x="created_at", y="temp_c")
        plt.xticks(rotation=30)
        plt.xlabel("Time (LA)")
        plt.ylabel("Temp (°C)")
        plt.tight_layout()
        st.pyplot(fig1, clear_figure=True)

    with right:
        st.subheader("Power vs time")
        fig2 = plt.figure(figsize=(7, 4))
        sns.lineplot(data=df, x="created_at", y="power_w")
        plt.xticks(rotation=30)
        plt.xlabel("Time (LA)")
        plt.ylabel("Power (W)")
        plt.tight_layout()
        st.pyplot(fig2, clear_figure=True)

# --- Auto refresh ---
time.sleep(REFRESH_SEC)
st.rerun()