# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns

# sns.set_style("whitegrid")

# # --- Load data ---
# temp = pd.read_csv("data/temperature.csv", parse_dates=["timestamp"])
# energy = pd.read_csv("data/energy.csv", parse_dates=["timestamp"])

# # Sort
# temp = temp.sort_values("timestamp").reset_index(drop=True)
# energy = energy.sort_values("timestamp").reset_index(drop=True)

# # Use cumulative energy directly (baseline always-on)
# energy["baseline_cum_Wh"] = energy["energy_Wh"]

# # --- Smart policy (threshold + hysteresis + min on/off) ---
# THIGH = 26.0   # turn ON at/above this
# TLOW  = 25.5   # turn OFF at/below this (hysteresis)
# MIN_HOLD_MIN = 2  # minimum minutes to stay in current state

# fan_on = []
# state = False
# last_switch_time = None

# for t, temp_c in zip(temp["timestamp"], temp["temp_c"]):
#     if last_switch_time is None:
#         last_switch_time = t

#     minutes_since = (t - last_switch_time).total_seconds() / 60.0
#     can_switch = minutes_since >= MIN_HOLD_MIN

#     if not state:
#         if can_switch and temp_c >= THIGH:
#             state = True
#             last_switch_time = t
#     else:
#         if can_switch and temp_c <= TLOW:
#             state = False
#             last_switch_time = t

#     fan_on.append(state)

# temp["fan_on_smart"] = fan_on

# # --- Build smart cumulative energy by masking baseline increments ---
# # 1) Baseline incremental energy between rows
# energy["delta_Wh"] = energy["baseline_cum_Wh"].diff().fillna(0)

# # 2) Get a fan_on_smart value for each energy timestamp
# temp_for_merge = temp[["timestamp", "fan_on_smart"]].sort_values("timestamp")
# energy = energy.sort_values("timestamp")

# energy = pd.merge_asof(
#     energy,
#     temp_for_merge,
#     on="timestamp",
#     direction="backward"
# )

# # If earliest energy timestamps come before temp starts, default OFF
# energy["fan_on_smart"] = energy["fan_on_smart"].fillna(False)

# # 3) Apply mask: when fan is OFF, energy does not increase
# energy["smart_delta_Wh"] = energy["delta_Wh"] * energy["fan_on_smart"].astype(int)

# # 4) Smart cumulative energy
# energy["smart_cum_Wh"] = energy["smart_delta_Wh"].cumsum()

# # --- Summary numbers ---
# baseline_total_Wh = energy["baseline_cum_Wh"].iloc[-1]
# smart_total_Wh = energy["smart_cum_Wh"].iloc[-1]
# savings_Wh = baseline_total_Wh - smart_total_Wh
# savings_pct = (savings_Wh / baseline_total_Wh) * 100 if baseline_total_Wh > 0 else 0

# # --- Cost + carbon impact (placeholders for now) ---
# RATE_PER_KWH = 0.30      # $/kWh (placeholder)
# CO2_PER_KWH  = 0.40      # kg CO2e / kWh (placeholder)

# baseline_kWh = baseline_total_Wh / 1000
# smart_kWh    = smart_total_Wh / 1000
# saved_kWh    = savings_Wh / 1000

# baseline_cost = baseline_kWh * RATE_PER_KWH
# smart_cost    = smart_kWh * RATE_PER_KWH
# saved_cost    = baseline_cost - smart_cost

# baseline_co2 = baseline_kWh * CO2_PER_KWH
# smart_co2    = smart_kWh * CO2_PER_KWH
# saved_co2    = baseline_co2 - smart_co2

# print("\n--- Impact ---")
# print(f"Baseline: ${baseline_cost:.3f}, {baseline_co2:.3f} kg CO2e")
# print(f"Smart:    ${smart_cost:.3f}, {smart_co2:.3f} kg CO2e")
# print(f"Saved:    ${saved_cost:.3f}, {saved_co2:.3f} kg CO2e")
# on_fraction = energy["fan_on_smart"].mean()

# print(f"ON fraction (smart): {on_fraction:.2%}")
# print(f"Baseline total: {baseline_total_Wh:.2f} Wh")
# print(f"Smart total:    {smart_total_Wh:.2f} Wh")
# print(f"Savings:        {savings_Wh:.2f} Wh ({savings_pct:.1f}%)")

# # --- Plot 1: Temperature ---
# plt.figure()
# sns.lineplot(data=temp, x="timestamp", y="temp_c", label="Temperature (°C)")
# plt.axhline(THIGH, linestyle="--", label="ON threshold")
# plt.axhline(TLOW, linestyle="--", label="OFF threshold")
# plt.title("Temperature vs Time")
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

# # --- Plot 2: Baseline vs Smart energy ---
# plt.figure()
# sns.lineplot(data=energy, x="timestamp", y="baseline_cum_Wh", label="Baseline (always on)")
# sns.lineplot(data=energy, x="timestamp", y="smart_cum_Wh", label="Smart (masked)")
# plt.title("Cumulative Energy (Wh): Baseline vs Smart")
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()