import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Flight Performance Envelope: 4 Cases
# A2A Max, A2A Min, Strike Max, Strike Min
# Dynamic pressure limits lower-right, max speed/Mach limits upper-right
# ============================================================

S = 400.0
AR = 3.5
e = 0.825
k = 1 / (np.pi * e * AR)

T_SL = 40000.0
M_max = 1.6
q_max = 800.0

V_stall_EAS_ref = 254.0
W_ref = 33953.47

rho0 = 0.002377
gamma = 1.4
R = 1716.0
T0 = 518.67
lapse = 0.00356616

cases = {
    "A2A Max": {"W": 33953.47, "CD0": 0.0144},
    "A2A Min": {"W": 22404.03, "CD0": 0.0144},
    "Strike Max": {"W": 36706.33, "CD0": 0.0137},
    "Strike Min": {"W": 22489.32, "CD0": 0.0137},
}

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

def make_envelope(case_name, W, CD0_clean):

    altitudes = np.linspace(0, 60000, 500)
    V_grid = np.linspace(100, 1900, 2500)

    stall_boundary = []
    mach_boundary = []
    q_boundary = []
    thrust_low_boundary = []
    thrust_high_boundary = []
    valid_altitudes = []

    V_stall_EAS = V_stall_EAS_ref * np.sqrt(W / W_ref)

    for h in altitudes:
        rho, a = atmosphere(h)
        sigma = rho / rho0

        V_stall_TAS = V_stall_EAS / np.sqrt(sigma)
        V_mach = M_max * a
        V_q = np.sqrt(2 * q_max / rho)

        T_available = T_SL * (0.7 * sigma + 0.3)

        feasible_speeds = []

        for V in V_grid:
            if V < V_stall_TAS:
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
            q_boundary.append(V_q)
            thrust_low_boundary.append(min(feasible_speeds))
            thrust_high_boundary.append(max(feasible_speeds))

    valid_altitudes = np.array(valid_altitudes)
    stall_boundary = np.array(stall_boundary)
    mach_boundary = np.array(mach_boundary)
    q_boundary = np.array(q_boundary)
    thrust_low_boundary = np.array(thrust_low_boundary)
    thrust_high_boundary = np.array(thrust_high_boundary)

    # Max speed/Mach boundary controls upper-right
    max_speed_boundary = np.minimum(thrust_high_boundary, mach_boundary)

    # Dynamic pressure controls lower-right where it is more restrictive
    right_boundary = np.minimum(q_boundary, max_speed_boundary)

    # Left side
    left_boundary = np.maximum(stall_boundary, thrust_low_boundary)

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

    plt.plot(stall_boundary, valid_altitudes, color="blue", linewidth=3,
             label="Stall Boundary", zorder=7)

    plt.plot(mach_boundary, valid_altitudes, color="orange", linestyle="--",
             linewidth=3, label="Mach 1.6 Boundary", zorder=5)

    plt.plot(q_boundary, valid_altitudes, color="brown", linestyle="-.",
             linewidth=3, label="Dynamic Pressure Limit", zorder=6)

    plt.plot(max_speed_boundary, valid_altitudes, color="green", linewidth=3,
             label="Max Speed Boundary", zorder=8)

    plt.plot(thrust_low_boundary, valid_altitudes, color="deeppink",
             linestyle="--", linewidth=3, alpha=0.75,
             label="Low-Speed Thrust Boundary", zorder=9)

    ceiling_alt = valid_altitudes[-1]
    plt.plot(
        [left_boundary[-1], right_boundary[-1]],
        [ceiling_alt, ceiling_alt],
        color="black",
        linewidth=3.5,
        label="Ceiling Boundary",
        zorder=10
    )

    plt.axhline(
        30000,
        color="purple",
        linestyle=":",
        linewidth=3,
        label="30,000 ft Mission Altitude",
        zorder=4
    )

    plt.xlabel("True Airspeed, V (ft/s)")
    plt.ylabel("Altitude (ft)")
    plt.title(f"Flight Performance Envelope - {case_name} Configuration")
    plt.grid(True)
    plt.legend(loc="upper left")
    plt.xlim(0, 1900)
    plt.ylim(0, 62000)
    plt.tight_layout()
    plt.show()

    rho_30k, a_30k = atmosphere(30000)
    sigma_30k = rho_30k / rho0
    V_stall_30k = V_stall_EAS / np.sqrt(sigma_30k)
    V_mach_30k = M_max * a_30k
    V_q_30k = np.sqrt(2 * q_max / rho_30k)

    print(f"\nKey Envelope Values - {case_name}")
    print("-------------------")
    print(f"W = {W:.2f} lb")
    print(f"S = {S:.1f} ft^2")
    print(f"CD0 = {CD0_clean:.4f}")
    print(f"k = {k:.5f}")
    print(f"T_SL = {T_SL:.0f} lbf")
    print(f"M_max = {M_max:.1f}")
    print(f"q_max = {q_max:.1f} lb/ft^2")
    print(f"Sea-level stall speed = {V_stall_EAS:.1f} ft/s EAS")
    print(f"30,000 ft stall speed = {V_stall_30k:.1f} ft/s TAS")
    print(f"30,000 ft Mach 1.6 speed = {V_mach_30k:.1f} ft/s")
    print(f"30,000 ft dynamic pressure speed limit = {V_q_30k:.1f} ft/s")
    print(f"Estimated ceiling boundary = {ceiling_alt:.0f} ft")

for case_name, data in cases.items():
    make_envelope(case_name, data["W"], data["CD0"])
