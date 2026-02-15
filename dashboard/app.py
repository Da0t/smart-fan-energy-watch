import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

sns.set_style("whitegrid")

st.set_page_config(page_title="Smart Fan Energy Watch", layout="wide")
st.title("Smart Fan Energy Watch")

# ---- Sidebar controls ----
st.sidebar.header("Smart policy settings")
THIGH = st.sidebar.slider("ON threshold (°C)", 20.0, 35.0, 26.0, 0.1)
TLOW  = st.sidebar.slider("OFF threshold (°C)", 18.0, 34.0, 25.5, 0.1)
MIN_HOLD_MIN = st.sidebar.slider("Min hold time (min)", 0, 10, 2, 1)

st.sidebar.header("Impact assumptions")
RATE_PER_KWH = st.sidebar.number_input("Electricity rate ($/kWh)", value=0.30, step=0.01)
CO2_PER_KWH  = st.sidebar.number_input("Carbon intensity (kg CO₂e/kWh)", value=0.40, step=0.01)

# ---- Load data ----
temp = pd.read_csv("data/temperature.csv", parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
energy = pd.read_csv("data/energy.csv", parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

energy["baseline_cum_Wh"] = energy["energy_Wh"]

# ---- Smart fan logic ----
fan_on = []
state = False
last_switch_time = None

for t, temp_c in zip(temp["timestamp"], temp["temp_c"]):
    if last_switch_time is None:
        last_switch_time = t

    minutes_since = (t - last_switch_time).total_seconds() / 60.0
    can_switch = minutes_since >= MIN_HOLD_MIN

    if not state:
        if can_switch and temp_c >= THIGH:
            state = True
            last_switch_time = t
    else:
        if can_switch and temp_c <= TLOW:
            state = False
            last_switch_time = t

    fan_on.append(state)

temp["fan_on_smart"] = fan_on

# ---- Masked energy ----
energy["delta_Wh"] = energy["baseline_cum_Wh"].diff().fillna(0)

temp_for_merge = temp[["timestamp", "fan_on_smart"]].sort_values("timestamp")
energy = pd.merge_asof(
    energy.sort_values("timestamp"),
    temp_for_merge,
    on="timestamp",
    direction="backward"
)
energy["fan_on_smart"] = energy["fan_on_smart"].fillna(False)

energy["smart_delta_Wh"] = energy["delta_Wh"] * energy["fan_on_smart"].astype(int)
energy["smart_cum_Wh"] = energy["smart_delta_Wh"].cumsum()

# ---- Metrics ----
baseline_total_Wh = float(energy["baseline_cum_Wh"].iloc[-1])
smart_total_Wh    = float(energy["smart_cum_Wh"].iloc[-1])
savings_Wh        = baseline_total_Wh - smart_total_Wh
savings_pct       = (savings_Wh / baseline_total_Wh) * 100 if baseline_total_Wh > 0 else 0.0

baseline_kWh = baseline_total_Wh / 1000
smart_kWh    = smart_total_Wh / 1000

baseline_cost = baseline_kWh * RATE_PER_KWH
smart_cost    = smart_kWh * RATE_PER_KWH

baseline_co2  = baseline_kWh * CO2_PER_KWH
smart_co2     = smart_kWh * CO2_PER_KWH

# ---- Display metrics ----
c1, c2, c3, c4 = st.columns(4)
c1.metric("Baseline energy (Wh)", f"{baseline_total_Wh:.2f}")
c2.metric("Smart energy (Wh)", f"{smart_total_Wh:.2f}")
c3.metric("Savings", f"{savings_Wh:.2f} Wh", f"{savings_pct:.1f}%")
c4.metric("Smart ON fraction", f"{energy['fan_on_smart'].mean():.2%}")

c5, c6 = st.columns(2)
c5.metric("Cost saved ($)", f"{(baseline_cost - smart_cost):.4f}")
c6.metric("CO₂ saved (kg)", f"{(baseline_co2 - smart_co2):.4f}")

# ---- Plots ----
left, right = st.columns(2)

with left:
    st.subheader("Temperature vs time")
    fig1 = plt.figure()
    sns.lineplot(data=temp, x="timestamp", y="temp_c")
    plt.axhline(THIGH, linestyle="--")
    plt.axhline(TLOW, linestyle="--")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig1)

with right:
    st.subheader("Cumulative energy: baseline vs smart")
    fig2 = plt.figure()
    sns.lineplot(data=energy, x="timestamp", y="baseline_cum_Wh", label="Baseline")
    sns.lineplot(data=energy, x="timestamp", y="smart_cum_Wh", label="Smart")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig2)

st.caption("Practice mode: swap in real CSVs later — dashboard stays the same.")