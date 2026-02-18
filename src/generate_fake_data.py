import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- Parameters ---
duration_minutes = 240  # 2 hours
start_time = datetime(2026, 2, 7, 14, 0, 0)

session_id = "trial1"

# --- Generate timestamps ---
timestamps = [start_time + timedelta(minutes=i) for i in range(duration_minutes)]

# --- Fake temperature (gradual rise + noise) ---
base_temp = 24
temp_trend = np.linspace(0, 3, duration_minutes)  # rises 3°C over 2 hours
noise = np.random.normal(0, 0.2, duration_minutes)

temps = base_temp + temp_trend + noise

temperature_df = pd.DataFrame({
    "session_id": session_id,
    "timestamp": timestamps,
    "temp_c": temps
})

# --- Fake energy (baseline always-on fan) ---
# Assume fan uses 5W constantly
power_watts = 5
energy_wh = np.cumsum([power_watts / 60] * duration_minutes)

energy_df = pd.DataFrame({
    "session_id": session_id,
    "timestamp": timestamps,
    "energy_Wh": energy_wh
})

# --- Save to data folder ---
temperature_df.to_csv("data/temperature.csv", index=False)
energy_df.to_csv("data/energy.csv", index=False)

print("Fake data generated successfully.")