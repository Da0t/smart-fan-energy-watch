import time
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from supabase import create_client

sns.set_style("whitegrid")

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

# --- Live area placeholders (so the page doesn't jump) ---
top = st.empty()
charts = st.container()

# --- A simple "polling" loop ---
# Streamlit reruns top-to-bottom; we trigger reruns with sleep + st.rerun()
if "live" not in st.session_state:
    st.session_state.live = True

with top:
    st.caption("Live mode: polling Supabase and refreshing automatically.")

df = fetch_latest(LIMIT, DEVICE_ID.strip() if DEVICE_ID.strip() else None)

if df.empty:
    st.warning("No rows found yet. Make sure ESP32 is inserting into `fan_readings` and device_id matches.")
else:
    # --- Metrics ---
    last = df.iloc[-1]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Latest time (LA)", last["created_at"].strftime("%Y-%m-%d %H:%M:%S"))
    c2.metric("Temp (°C)", f"{float(last['temp_c']):.2f}")
    c3.metric("Power (W)", f"{float(last['power_w']):.3f}")
    c4.metric("Fan mode", str(last.get("fan_mode", "")))

    # --- Table ---
    st.subheader("Latest readings")
    st.dataframe(df.tail(50), use_container_width=True)

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