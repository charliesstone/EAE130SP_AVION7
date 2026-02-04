import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


 
# Inputs you must set
 
AR = 4.5  # wing aspect ratio OpenVSP

CD0_clean = 0.0190  # Clean CD0 OpenVSP 

#delta CD0 from slides
dCD0_takeoff_flaps = 0.015   # 0.010–0.020
dCD0_landing_flaps = 0.065   # 0.055–0.075
dCD0_gear          = 0.020   # 0.015–0.025

# Oswald e by stage from slides
e_clean   = 0.825  # 0.80–0.85
e_takeoff = 0.775  # 0.75–0.80
e_landing = 0.725  # 0.70–0.75

# CL max assumptions from raskom 
CLmax_clean   = 1.6
CLmax_takeoff = 2.0
CLmax_landing = 2.3

 
# configuration table

configs = np.array([
    "Clean",
    "Takeoff flaps",
    "Takeoff flaps",
    "Landing flaps",
    "Landing flaps"
])

dCD0_flaps = np.array([
    0.0,
    dCD0_takeoff_flaps,
    dCD0_takeoff_flaps,
    dCD0_landing_flaps,
    dCD0_landing_flaps
])

dCD0_gear = np.array([
    0.0,
    0.0,
    dCD0_gear,
    0.0,
    dCD0_gear
])

e_values = np.array([
    e_clean,
    e_takeoff,
    e_takeoff,
    e_landing,
    e_landing
])

CL_max = np.array([
    CLmax_clean,
    CLmax_takeoff,
    CLmax_takeoff,
    CLmax_landing,
    CLmax_landing
])

# pandas dataframe
config_df = pd.DataFrame({
    "config": configs,
    "dCD0_flaps": dCD0_flaps,
    "dCD0_gear": dCD0_gear,
    "e": e_values,
    "CL_max": CL_max
})


# Compute CD0 for each configuration using delta CD0
config_df["CD0_config"] = CD0_clean + config_df["dCD0_flaps"] + config_df["dCD0_gear"]

# induced-drag factor k for each configuration (since e changes with flaps)
config_df["k"] = 1.0 / (math.pi * AR * config_df["e"])

print("\n=== Final CD0 per configuration (Clean + ΔCD0) ===")
print(config_df[["config", "CD0_config", "dCD0_flaps", "dCD0_gear", "e", "k"]].to_string(index=False))

 
# drag polar plot 
 
plt.figure()

for _, row in config_df.iterrows():
    CL = np.linspace(-3.0, row["CL_max"], 900)  # CL from -4 to CLmax
    CD = row["CD0_config"] + row["k"] * (CL**2) 
    plt.plot(CD, CL, linewidth=1, label=row["config"])


plt.xlabel("C_D")
plt.ylabel("C_L")
plt.xlim(0, 0.30)
plt.xticks([0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30])
plt.ylim(-1.5, 1.5)
plt.title("Drag Polar")
plt.grid(True)
plt.legend()
plt.show()

