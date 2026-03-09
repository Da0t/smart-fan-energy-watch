import time
from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Smart Fan Energy Watch", page_icon="🌀", layout="wide")

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');
      :root {
        --bg: #07111f;
        --card: #0d1b2a;
        --text: #e6edf7;
        --muted: #9fb3c8;
        --border: #1f3347;
        --temp: #f59e0b;
        --power: #22d3ee;
        --save: #22c55e;
        --warn: #ef4444;
        --font-display: "Space Grotesk", "Inter", sans-serif;
        --font-body: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      .stApp {
        background:
          radial-gradient(1200px 500px at 12% -20%, #11325566, transparent 55%),
          radial-gradient(1000px 450px at 88% -30%, #0f766e55, transparent 50%),
          var(--bg);
        font-family: var(--font-body);
      }
      h1, h2, h3, [data-testid="stSidebarHeader"] {
        font-family: var(--font-display);
        letter-spacing: -0.01em;
      }
      [data-testid="stMetric"] {
        background: linear-gradient(160deg, #102238 0%, var(--card) 100%);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 6px;
      }
      [data-testid="stMetricLabel"] {
        font-family: var(--font-body);
        font-weight: 500;
      }
      [data-testid="stMetricValue"] {
        font-family: var(--font-display);
        font-size: 2.15rem;
        line-height: 1.1;
      }
      .section-title {
        color: var(--text);
        font-size: 1.05rem;
        font-weight: 700;
        margin: 8px 0 4px 0;
        font-family: var(--font-display);
      }
      .section-title-lg-top {
        margin-top: 24px;
      }
      .section-subtitle {
        color: var(--muted);
        font-size: 0.88rem;
        margin-bottom: 8px;
      }
      .kpi-row-gap-tight {
        margin-top: -8px;
      }
      .status-pill {
        display: inline-block;
        border: 1px solid var(--border);
        border-radius: 999px;
        color: var(--muted);
        padding: 4px 10px;
        font-size: 0.78rem;
        margin-right: 6px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Smart Fan Energy Watch")

# --- Secrets ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
sb = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- Sidebar controls ---
st.sidebar.header("Live settings")
REFRESH_SEC = st.sidebar.slider("Refresh interval (seconds)", 1, 10, 2)
DEVICE_ID = st.sidebar.text_input("device_id filter (optional)", value="esp32_01")
LIMIT = st.sidebar.slider("Rows to display", 50, 1000, 200)
WINDOW_HOURS = st.sidebar.slider("Analysis window (hours)", 1, 168, 24)
MAX_GAP_MIN = st.sidebar.slider("Ignore gaps larger than (minutes)", 1, 180, 30)

st.sidebar.header("Savings assumptions")
BASELINE_W = st.sidebar.number_input(
    "Baseline power (W) (e.g., HIGH mode)", min_value=0.0, value=2.949, step=0.1
)
PRICE_PER_KWH = st.sidebar.number_input(
    "Electricity price ($/kWh)", min_value=0.0, value=0.35, step=0.01
)


# --- Helper: fetch latest rows ---
@st.cache_data(ttl=1)
def fetch_latest(limit: int, device_id: str | None):
    q = (
        sb.table("fan_readings")
        .select("created_at,temp_c,power_w,fan_mode,device_id")
        .order("created_at", desc=True)
        .limit(limit)
    )
    if device_id:
        q = q.eq("device_id", device_id)
    data = q.execute().data
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df["created_at"] = (
        pd.to_datetime(df["created_at"], utc=True)
        .dt.tz_convert("America/Los_Angeles")
        .dt.tz_localize(None)
    )
    df = df.sort_values("created_at")
    return df


def _interval_hours(df: pd.DataFrame, time_col: str, max_gap_seconds: float | None) -> pd.Series:
    dt_h = df[time_col].diff().dt.total_seconds().clip(lower=0) / 3600.0
    if max_gap_seconds is not None:
        dt_h = dt_h.where(dt_h * 3600.0 <= max_gap_seconds, 0.0)
    return dt_h.fillna(0)


def energy_kwh_from_power(
    df: pd.DataFrame, time_col="created_at", power_col="power_w", max_gap_seconds: float | None = None
) -> float:
    d = df.copy().sort_values(time_col)
    dt_h = _interval_hours(d, time_col, max_gap_seconds)
    return float((d[power_col].astype(float) * dt_h).sum() / 1000.0)


def baseline_kwh_constant(
    df: pd.DataFrame, baseline_watts: float, time_col="created_at", max_gap_seconds: float | None = None
) -> float:
    d = df.copy().sort_values(time_col)
    dt_h = _interval_hours(d, time_col, max_gap_seconds)
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


@st.cache_data(ttl=1800)
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
    return c * 9.0 / 5.0 + 32.0


# --- Live status ---
df_all = fetch_latest(LIMIT, DEVICE_ID.strip() if DEVICE_ID.strip() else None)
if not df_all.empty:
    cutoff = df_all["created_at"].max() - pd.Timedelta(hours=WINDOW_HOURS)
    df = df_all[df_all["created_at"] >= cutoff].copy()
else:
    df = df_all

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

status_cols = st.columns([1.1, 1.1, 2.8])
status_cols[0].markdown("<span class='status-pill'>Live polling</span>", unsafe_allow_html=True)
status_cols[1].markdown(
    f"<span class='status-pill'>Refresh: {REFRESH_SEC}s</span>",
    unsafe_allow_html=True,
)
status_cols[2].markdown(
    f"<span class='status-pill'>Device: {DEVICE_ID.strip() or 'all devices'}</span>",
    unsafe_allow_html=True,
)

if df.empty:
    st.warning("No rows found yet. Make sure ESP32 is inserting into `fan_readings` and device_id matches.")
else:
    last = df.iloc[-1]
    indoor_f = c_to_f(float(last["temp_c"]))

    max_gap_seconds = float(MAX_GAP_MIN * 60)
    dt_s = df["created_at"].diff().dt.total_seconds().clip(lower=0).fillna(0)
    active_dt_s = dt_s.where(dt_s <= max_gap_seconds, 0.0)

    window_seconds = float(active_dt_s.sum())
    avg_interval_seconds = df["created_at"].diff().dt.total_seconds().dropna().mean()
    avg_interval_seconds = float(avg_interval_seconds) if pd.notna(avg_interval_seconds) else 0.0

    actual_kwh = energy_kwh_from_power(df, max_gap_seconds=max_gap_seconds)
    base_kwh = baseline_kwh_constant(df, float(BASELINE_W), max_gap_seconds=max_gap_seconds)
    saved_kwh = max(0.0, base_kwh - actual_kwh)
    pct_saved = (saved_kwh / base_kwh * 100.0) if base_kwh > 0 else 0.0

    cost_used = actual_kwh * float(PRICE_PER_KWH)
    cost_saved = saved_kwh * float(PRICE_PER_KWH)

    st.markdown("<div class='section-title'>Live KPIs</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-subtitle'>Primary performance indicators for the current telemetry window.</div>",
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Indoor Temp", f"{indoor_f:.1f}°F")
    k2.metric("Current Power", f"{float(last['power_w']):.2f} W")
    k3.metric("Fan Mode", str(last.get("fan_mode", "")))
    k4.metric("Savings", f"{pct_saved:.1f}%", delta=f"${cost_saved:.2f}")

    st.markdown("<div class='kpi-row-gap-tight'></div>", unsafe_allow_html=True)
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Used Energy", f"{actual_kwh:.4f} kWh")
    d2.metric("Window", format_duration(window_seconds))
    d3.metric("Avg Sample Interval", f"{avg_interval_seconds:.1f}s")
    d4.metric("Last Reading", last["created_at"].strftime("%H:%M:%S"))

    st.caption(
        f"Baseline assumes constant {float(BASELINE_W):.3f} W over this window. "
        f"Estimated cost saved: ${cost_saved:.2f} at ${float(PRICE_PER_KWH):.2f}/kWh."
    )

    left, right = st.columns([1.7, 1.1])

    with left:
        st.markdown("<div class='section-title section-title-lg-top'>Latest Readings</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>Most recent 50 points for operational monitoring.</div>",
            unsafe_allow_html=True,
        )
        latest = df[["created_at", "temp_c", "power_w", "fan_mode", "device_id"]].tail(50).copy()
        latest = latest.rename(
            columns={
                "created_at": "Time",
                "temp_c": "Temp (°C)",
                "power_w": "Power (W)",
                "fan_mode": "Mode",
                "device_id": "Device",
            }
        )
        st.dataframe(
            latest,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Temp (°C)": st.column_config.NumberColumn(format="%.1f"),
                "Power (W)": st.column_config.NumberColumn(format="%.3f"),
            },
        )

        with st.expander("Show full raw table"):
            st.dataframe(df, use_container_width=True)

    with right:
        st.markdown("<div class='section-title section-title-lg-top'>Mode Breakdown</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>Time-weighted share of each fan mode in this window.</div>",
            unsafe_allow_html=True,
        )

        d = df.copy().sort_values("created_at")
        d["dt_s"] = d["created_at"].diff().dt.total_seconds().clip(lower=0).fillna(0)
        d["dt_s"] = d["dt_s"].where(d["dt_s"] <= max_gap_seconds, 0.0)
        d["mode_for_interval"] = d["fan_mode"].shift(1).fillna(d["fan_mode"])

        mode_seconds = d.groupby("mode_for_interval")["dt_s"].sum().sort_values(ascending=False)
        total_seconds = mode_seconds.sum()

        if total_seconds > 0:
            mode_pct = (mode_seconds / total_seconds * 100.0).round(1)
            mode_table = pd.DataFrame({"seconds": mode_seconds.round(1), "percent": mode_pct})
            st.dataframe(mode_table, use_container_width=True)

            mode_chart = px.bar(
                x=mode_pct.values,
                y=mode_pct.index.astype(str),
                orientation="h",
                labels={"x": "Percent of time (%)", "y": "Mode"},
                color=mode_pct.values,
                color_continuous_scale="Tealgrn",
            )
            mode_chart.update_layout(
                margin=dict(l=10, r=10, t=6, b=10),
                height=250,
                coloraxis_showscale=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#dbe7f3"),
            )
            st.plotly_chart(mode_chart, use_container_width=True)
        else:
            st.info("Not enough time range yet to compute mode breakdown.")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='section-title'>Temperature vs Time</div>", unsafe_allow_html=True)
        temp_fig = go.Figure()
        temp_fig.add_trace(
            go.Scatter(
                x=df["created_at"],
                y=df["temp_c"],
                mode="lines",
                name="Indoor temp (°C)",
                line=dict(color="#f59e0b", width=3),
            )
        )

        if med_threshold_f is not None:
            med_c = (med_threshold_f - 32.0) * 5.0 / 9.0
            high_c = (high_threshold_f - 32.0) * 5.0 / 9.0
            temp_fig.add_hline(y=med_c, line_dash="dot", line_color="#38bdf8", annotation_text="MED threshold")
            temp_fig.add_hline(y=high_c, line_dash="dash", line_color="#ef4444", annotation_text="HIGH threshold")

        temp_fig.update_layout(
            xaxis_title="Time (LA)",
            yaxis_title="Temp (°C)",
            margin=dict(l=10, r=10, t=8, b=10),
            height=330,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#dbe7f3"),
            legend=dict(orientation="h", y=1.05, x=0),
        )
        st.plotly_chart(temp_fig, use_container_width=True)

    with c2:
        st.markdown("<div class='section-title'>Power vs Time</div>", unsafe_allow_html=True)
        power_fig = go.Figure()
        power_fig.add_trace(
            go.Scatter(
                x=df["created_at"],
                y=df["power_w"],
                mode="lines",
                name="Power (W)",
                line=dict(color="#22d3ee", width=3),
                fill="tozeroy",
                fillcolor="rgba(34, 211, 238, 0.18)",
            )
        )
        power_fig.update_layout(
            xaxis_title="Time (LA)",
            yaxis_title="Power (W)",
            margin=dict(l=10, r=10, t=8, b=10),
            height=330,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#dbe7f3"),
            legend=dict(orientation="h", y=1.05, x=0),
        )
        st.plotly_chart(power_fig, use_container_width=True)

# --- Auto refresh ---
time.sleep(REFRESH_SEC)
st.rerun()
