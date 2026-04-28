import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Part 4: Flight Performance Envelope
# Team 7 AVION
# ============================================================

# Aircraft inputs
S = 400.0                  # ft^2
W = 36767.43               # lb, A2A max/takeoff weight
CD0_clean = 0.0144
AR = 3.5
e = 0.825
k = 1 / (np.pi * e * AR)

T_SL = 40000.0             # lbf, sea-level thrust
M_max = 1.6
V_stall_EAS = 254.0        # ft/s, from V-n diagram

# Sea-level standard atmosphere
rho0 = 0.002377            # slug/ft^3
gamma = 1.4
R = 1716.0                 # ft*lbf/(slug*R)
T0 = 518.67                # Rankine
lapse = 0.00356616         # R/ft

# -----------------------------
# Atmosphere model
# -----------------------------
def atmosphere(h_ft):
    if h_ft <= 36089:
        T = T0 - lapse * h_ft
        rho = rho0 * (T / T0) ** 4.2561
    else:
        T = 389.97
        rho_36k = rho0 * (T / T0) ** 4.2561
        rho = rho_36k * np.exp(-(h_ft - 36089) / 20806)

    a = np.sqrt(gamma * R * T)
    return rho, a

# -----------------------------
# Sweep altitude and speed
# -----------------------------
altitudes = np.linspace(0, 60000, 350)
V_grid = np.linspace(100, 1900, 1500)

stall_boundary = []
mach_boundary = []
thrust_low_boundary = []
thrust_high_boundary = []
valid_altitudes = []

for h in altitudes:
    rho, a = atmosphere(h)
    sigma = rho / rho0

    V_stall_TAS = V_stall_EAS / np.sqrt(sigma)
    V_mach = M_max * a

    # Jet thrust available model
    T_available = T_SL * (0.7 * sigma + 0.3)

    feasible_speeds = []

    for V in V_grid:
        if V < V_stall_TAS or V > V_mach:
            continue

        q = 0.5 * rho * V**2
        CL = W / (q * S)
        CD = CD0_clean + k * CL**2
        D = q * S * CD

        if T_available >= D:
            feasible_speeds.append(V)

    if len(feasible_speeds) > 0:
        valid_altitudes.append(h)
        stall_boundary.append(V_stall_TAS)
        mach_boundary.append(V_mach)
        thrust_low_boundary.append(min(feasible_speeds))
        thrust_high_boundary.append(max(feasible_speeds))

valid_altitudes = np.array(valid_altitudes)
stall_boundary = np.array(stall_boundary)
mach_boundary = np.array(mach_boundary)
thrust_low_boundary = np.array(thrust_low_boundary)
thrust_high_boundary = np.array(thrust_high_boundary)

right_boundary = np.minimum(mach_boundary, thrust_high_boundary)
left_boundary = np.maximum(stall_boundary, thrust_low_boundary)

# Smooth right boundary
right_boundary = np.maximum.accumulate(right_boundary[::-1])[::-1]

# -----------------------------
# Plot
# -----------------------------
plt.figure(figsize=(11, 7))

plt.fill_betweenx(
    valid_altitudes,
    left_boundary,
    right_boundary,
    color="blue",
    alpha=0.12,
    label="Achievable Flight Envelope",
    zorder=1
)

plt.plot(
    stall_boundary,
    valid_altitudes,
    color="blue",
    linewidth=3,
    zorder=6,
    label="Stall Boundary"
)

plt.plot(
    mach_boundary,
    valid_altitudes,
    color="orange",
    linewidth=3,
    linestyle="--",
    zorder=5,
    label="Mach 1.6 Boundary"
)

plt.plot(
    right_boundary,
    valid_altitudes,
    color="green",
    linewidth=3,
    zorder=4,
    label="Max Speed Boundary"
)

plt.plot(
    thrust_low_boundary,
    valid_altitudes,
    color="deeppink",
    linestyle="--",
    linewidth=3,
    alpha=0.75,
    zorder=7,
    label="Low-Speed Thrust Boundary"
)

# Ceiling boundary, slightly below the top so it is visible
ceiling_plot_alt = valid_altitudes[-1] - 500

plt.plot(
    [left_boundary[-1], right_boundary[-1]],
    [ceiling_plot_alt, ceiling_plot_alt],
    color="black",
    linestyle="-",
    linewidth=3.5,
    zorder=10,
    label="Ceiling Boundary"
)

# Mission altitude line in dark purple
plt.axhline(
    30000,
    color="purple",
    linestyle=":",
    linewidth=3,
    zorder=9,
    label="30,000 ft Mission Altitude"
)

plt.xlabel("Airspeed, V (ft/s)")
plt.ylabel("Altitude (ft)")
plt.title("Flight Performance Envelope")
plt.grid(True)
plt.legend(loc="upper left")
plt.xlim(0, 1900)
plt.ylim(0, 62000)
plt.tight_layout()
plt.show()

# -----------------------------
# Key output values
# -----------------------------
ceiling = valid_altitudes[-1]

rho_30k, a_30k = atmosphere(30000)
sigma_30k = rho_30k / rho0
V_stall_30k = V_stall_EAS / np.sqrt(sigma_30k)
V_mach_30k = M_max * a_30k

print("Key Envelope Values")
print("-------------------")
print(f"W = {W:.2f} lb")
print(f"S = {S:.1f} ft^2")
print(f"CD0 = {CD0_clean:.4f}")
print(f"k = {k:.5f}")
print(f"T_SL = {T_SL:.0f} lbf")
print(f"M_max = {M_max:.1f}")
print(f"Sea-level stall speed = {V_stall_EAS:.1f} ft/s EAS")
print(f"30,000 ft stall speed = {V_stall_30k:.1f} ft/s TAS")
print(f"30,000 ft Mach 1.6 speed = {V_mach_30k:.1f} ft/s")
print(f"Estimated ceiling boundary = {ceiling:.0f} ft")

