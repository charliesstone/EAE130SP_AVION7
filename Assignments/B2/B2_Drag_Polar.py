import numpy as np
import matplotlib.pyplot as plt

# =========================================
# Aircraft / Geometry Inputs
# =========================================
S_ref = 400.0          # ft^2
AR = 3.5

# Clean parasite drag cases
CD0_clean_A2A = 0.0144
CD0_clean_STR = 0.0137

# Effective flap / gear increments used in final drag polar plots
dCD0_takeoff_flaps = 0.0157
dCD0_landing_flaps = 0.0633
dCD0_gear = 0.009

# Oswald efficiencies
e_clean   = 0.825
e_takeoff = 0.775
e_landing = 0.725

# Wave drag from VSPAero at Mach 1.6
CD_wave = 0.017

# =========================================
# Representative flight-condition inputs
# =========================================
W_A2A = 36767.43   # lb
W_STR = 37047.0    # lb

rho_takeoff = 0.002377   # slug/ft^3
rho_landing = 0.002000   # slug/ft^3

V_takeoff = 250.0   # ft/s
V_landing = 220.0   # ft/s

# =========================================
# Camber / asymmetric polar shift values
# Minimum drag occurs at CL = CL_min_drag
# =========================================
CLmin_clean = 0.25
CLmin_to    = 0.55
CLmin_ld    = 0.85

# =========================================
# Functions
# =========================================
def compute_CL(W, rho, V, S):
    return W / (0.5 * rho * V**2 * S)

def compute_CDi(CL, e, AR):
    return CL**2 / (np.pi * e * AR)

def total_drag(CL, CD0, e, AR, CL_min_drag=0.0, CD_trim=0.0, CD_wave=0.0):
    K = 1.0 / (np.pi * e * AR)
    return CD0 + CD_trim + CD_wave + K * (CL - CL_min_drag)**2

def drag_polar_curve(CL_array, CD0, e, AR, CL_min_drag=0.0, CD_trim=0.0, CD_wave=0.0):
    K = 1.0 / (np.pi * e * AR)
    return CD0 + CD_trim + CD_wave + K * (CL_array - CL_min_drag)**2

# =========================================
# Compute CL and induced drag for each case
# =========================================
# A2A
CL_TO_A2A = compute_CL(W_A2A, rho_takeoff, V_takeoff, S_ref)
CL_LD_A2A = compute_CL(W_A2A, rho_landing, V_landing, S_ref)

CDi_TO_A2A = compute_CDi(CL_TO_A2A, e_takeoff, AR)
CDi_LD_A2A = compute_CDi(CL_LD_A2A, e_landing, AR)

# Strike
CL_TO_STR = compute_CL(W_STR, rho_takeoff, V_takeoff, S_ref)
CL_LD_STR = compute_CL(W_STR, rho_landing, V_landing, S_ref)

CDi_TO_STR = compute_CDi(CL_TO_STR, e_takeoff, AR)
CDi_LD_STR = compute_CDi(CL_LD_STR, e_landing, AR)

# =========================================
# Build zero-lift drag coefficients
# =========================================
def build_config_CD0(CD0_clean):
    return {
        "clean": CD0_clean,
        "to_gear_up": CD0_clean + dCD0_takeoff_flaps,
        "to_gear_down": CD0_clean + dCD0_takeoff_flaps + dCD0_gear,
        "ld_gear_up": CD0_clean + dCD0_landing_flaps,
        "ld_gear_down": CD0_clean + dCD0_landing_flaps + dCD0_gear
    }

CD0s_A2A = build_config_CD0(CD0_clean_A2A)
CD0s_STR = build_config_CD0(CD0_clean_STR)

# =========================================
# Print induced drag results
# =========================================
print("===== A2A =====")
print(f"Takeoff CL  = {CL_TO_A2A:.4f}")
print(f"Landing CL  = {CL_LD_A2A:.4f}")
print(f"Takeoff CDi = {CDi_TO_A2A:.4f}")
print(f"Landing CDi = {CDi_LD_A2A:.4f}")

print("\n===== Strike =====")
print(f"Takeoff CL  = {CL_TO_STR:.4f}")
print(f"Landing CL  = {CL_LD_STR:.4f}")
print(f"Takeoff CDi = {CDi_TO_STR:.4f}")
print(f"Landing CDi = {CDi_LD_STR:.4f}")

# =========================================
# Plot drag polars
# =========================================
CL_range = np.linspace(-1.5, 2.2, 500)

def plot_drag_polars(CD0s, title, include_wave=False):
    wave = CD_wave if include_wave else 0.0

    CD_clean = drag_polar_curve(CL_range, CD0s["clean"], e_clean, AR,
                                CL_min_drag=CLmin_clean, CD_trim=0.0, CD_wave=wave)
    CD_to_up = drag_polar_curve(CL_range, CD0s["to_gear_up"], e_takeoff, AR,
                                CL_min_drag=CLmin_to, CD_trim=0.0, CD_wave=wave)
    CD_to_dn = drag_polar_curve(CL_range, CD0s["to_gear_down"], e_takeoff, AR,
                                CL_min_drag=CLmin_to, CD_trim=0.0, CD_wave=wave)
    CD_ld_up = drag_polar_curve(CL_range, CD0s["ld_gear_up"], e_landing, AR,
                                CL_min_drag=CLmin_ld, CD_trim=0.0, CD_wave=wave)
    CD_ld_dn = drag_polar_curve(CL_range, CD0s["ld_gear_down"], e_landing, AR,
                                CL_min_drag=CLmin_ld, CD_trim=0.0, CD_wave=wave)

    plt.figure(figsize=(8, 6))

    plt.plot(CD_clean, CL_range, label='Clean')
    plt.plot(CD_to_up, CL_range, label='Takeoff flaps + gear up')
    plt.plot(CD_to_dn, CL_range, label='Takeoff flaps + gear down')
    plt.plot(CD_ld_up, CL_range, label='Landing flaps + gear up')
    plt.plot(CD_ld_dn, CL_range, label='Landing flaps + gear down')

    # Representative markers
    CL_clean_marker = 0.36
    CD_clean_marker = drag_polar_curve(
        np.array([CL_clean_marker]),
        CD0s["clean"],
        e_clean,
        AR,
        CL_min_drag=CLmin_clean,
        CD_wave=wave
    )[0]

    CL_to_marker = 1.2
    CD_to_marker = drag_polar_curve(
        np.array([CL_to_marker]),
        CD0s["to_gear_up"],
        e_takeoff,
        AR,
        CL_min_drag=CLmin_to,
        CD_wave=wave
    )[0]

    CL_ld_marker = 1.89
    CD_ld_marker = drag_polar_curve(
        np.array([CL_ld_marker]),
        CD0s["ld_gear_up"],
        e_landing,
        AR,
        CL_min_drag=CLmin_ld,
        CD_wave=wave
    )[0]
    plt.scatter(CD_clean_marker, CL_clean_marker, label='3° cruise')
    plt.scatter(CD_to_marker, CL_to_marker, label='10° takeoff')
    plt.scatter(CD_ld_marker, CL_ld_marker, label='15° landing', color = 'red')

    plt.xlabel('C_D')
    plt.ylabel('C_L')
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.xlim(0.0, 0.30)
    plt.ylim(-0.75, 2.0)
    plt.tight_layout()
    plt.show()

# =========================================
# Generate plots
# =========================================
plot_drag_polars(CD0s_A2A, "Drag Polar - A2A")
plot_drag_polars(CD0s_STR, "Drag Polar - Strike")

plot_drag_polars(CD0s_A2A, "Drag Polar - A2A (Mach 1.6 with Wave Drag)", include_wave=True)
plot_drag_polars(CD0s_STR, "Drag Polar - Strike (Mach 1.6 with Wave Drag)", include_wave=True)

# =========================================
# Print configuration CD0 values
# =========================================
print("\n=== Configuration CD0 values ===")
print("A2A:")
for config, CD0 in CD0s_A2A.items():
    print(f"  {config}: {CD0:.6f}")

print("Strike:")
for config, CD0 in CD0s_STR.items():
    print(f"  {config}: {CD0:.6f}")

# =========================================
# Print minimum-drag CL values used
# =========================================
print("\n=== CL at Minimum Drag (camber shift) ===")
print(f"Clean   CL_min_drag = {CLmin_clean:.3f}")
print(f"Takeoff CL_min_drag = {CLmin_to:.3f}")
print(f"Landing CL_min_drag = {CLmin_ld:.3f}")