# for Dash Mach 1.6

import math
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# 0) CONSTANTS / UNIT CONVERSIONS
# -----------------------------
kg_to_lb = 2.2046226218

# -----------------------------
# 1) INPUTS FROM  WEIGHT CODE 
# -----------------------------
# Crew
n_pilots = 1
pilot_mass_kg = 95.0
W_crew = n_pilots * pilot_mass_kg * kg_to_lb  # [lb]

# Avionics + engine weight handling
W_avionics = 2500.0   # [lb]
W_engine   = 3830.0   # [lb]  y

# Weapons
W_AIM120 = 350.0
W_AIM9X  = 190.0
W_MK83_JDAM = 1050.0

stores_install_fraction = 0.06
def add_installation(W_payload_total):
    weapons_only = max(W_payload_total - W_avionics, 0.0)
    return W_payload_total + stores_install_fraction * weapons_only

W_payload_AA = add_installation(W_avionics + 6*W_AIM120 + 2*W_AIM9X)
W_payload_STRIKE = add_installation(W_avionics + 4*W_MK83_JDAM + 2*W_AIM9X)

# Choose governing payload 
W_payload_case = max(W_payload_AA, W_payload_STRIKE)

# Mission / fuel fraction inputs (your values)
R_nmi     = 4000.0
E_hr      = 0.5
c_tsfc    = 0.75
V_ms      = 548.0
V_kt      = V_ms * 1.9438444924  # knots

segment_fracs = {
    "Takeoff": 0.990,
    "Climb":   0.980,
    "Descent": 0.990,
    "Landing": 0.995
}
reserve_factor = 1.06

# Empty weight fraction correlation
A = 2.392
C = -0.13

# Parasite drag 
CD0_total = 0.0190

# Reference wing area (only used to define S sweep)
S_ref_ft2 = 573.0

# -----------------------------
# 2) DASH CONDITION (constraint)
# -----------------------------
M_dash = 1.6
alt_ft = 30000.0

# -----------------------------
# 3) MISSION/CRUISE CONDITION (for fuel fraction L/D estimate)
# -----------------------------
M_mission = 0.85

# -----------------------------
# 4) SIMPLE AERO MODEL FOR DASH CONSTRAINT
#    CD = CD0 + k*CL^2 with k = 1/(pi*e*AR)
# -----------------------------
AR = 3.5     # <-- EDIT if you know your wing AR
e  = 0.85    # <-- EDIT if you know your Oswald e
k_ind = 1.0 / (math.pi * e * AR)

# -----------------------------
# 5) ISA atmosphere (English) 
# -----------------------------
def isa_atm_english(alt_ft):
    g0 = 32.174
    R  = 1716.0
    gamma = 1.4

    if alt_ft <= 36089.0:
        T0 = 518.67
        P0 = 2116.22
        L  = -0.00356616  # R/ft
        T  = T0 + L * alt_ft
        P  = P0 * (T / T0) ** (-g0 / (L * R))
    else:
        T = 389.97
        P = 472.68 * math.exp(-g0 * (alt_ft - 36089.0) / (R * T))

    rho = P / (R * T)
    a   = math.sqrt(gamma * R * T)
    return T, a, rho

T_R, a_ft_s, rho = isa_atm_english(alt_ft)

# Dynamic pressure for dash constraint
V_dash_ft_s = M_dash * a_ft_s
q_dash = 0.5 * rho * V_dash_ft_s**2  # lbf/ft^2

# Dynamic pressure for mission L/D estimate in fuel fraction
V_mission_ft_s = M_mission * a_ft_s
q_mission = 0.5 * rho * V_mission_ft_s**2  # lbf/ft^2

# -----------------------------
# 6) DASH CONSTRAINT: required T/W as a function of W/S
#    T/W = q*CD0/(W/S) + k*(W/S)/q
# -----------------------------
def TW_req_dash(WS):
    return (q_dash * CD0_total) / WS + (k_ind * WS) / q_dash

# -----------------------------
# 7) UPDATED FUEL FRACTION inside INNER LOOP    
# -----------------------------
def fuel_fraction_total(W0, S):
    WS = W0 / S

    CL = WS / q_mission
    CD = CD0_total + k_ind * CL**2
    LD = max(CL / CD, 1.0)
    LD_eff = 0.94 * LD  

    Wf_Wi_cruise = math.exp(-R_nmi * c_tsfc / (V_kt * LD_eff))
    Wf_Wi_loiter = math.exp(-E_hr * c_tsfc / LD_eff)

    W_end_W0 = 1.0
    for frac in segment_fracs.values():
        W_end_W0 *= frac
    W_end_W0 *= Wf_Wi_cruise
    W_end_W0 *= Wf_Wi_loiter

    fuel_frac_mission = 1.0 - W_end_W0
    Wf_W0_total = reserve_factor * fuel_frac_mission

    return max(0.01, min(Wf_W0_total, 0.70))

# -----------------------------
# 8) INNER LOOP: converge W0 at fixed (S, T)
# -----------------------------
def solve_weight_inner(S, T, W0_guess=80000.0, tol_W=1e-4, max_inner=200):
    W0 = float(W0_guess)
    for it in range(max_inner):
        We_W0 = A * (W0 ** C)
        Wf_W0 = fuel_fraction_total(W0, S)

        denom = 1.0 - We_W0 - Wf_W0
        if denom <= 0.05:
            denom = 0.05

        W0_new_core = (W_payload_case + W_crew) / denom
        W0_new = W0_new_core + W_engine  

        if abs(W0_new - W0) / max(W0, 1.0) < tol_W:
            return W0_new, it + 1
        W0 = W0_new

    return W0, max_inner

# -----------------------------
# 9) OUTER LOOP: converge T at fixed S
# -----------------------------
def solve_thrust_outer(S, T_guess=15000.0, tol_T=1e-4, tol_W=1e-4,
                       max_outer=100, max_inner=200):
    T = float(T_guess)
    W0_guess = 80000.0

    for it in range(max_outer):
        W0, inner_iters = solve_weight_inner(S, T, W0_guess=W0_guess,
                                             tol_W=tol_W, max_inner=max_inner)

        WS = W0 / S
        TW_req = TW_req_dash(WS)
        T_new = TW_req * W0

        if abs(T_new - T) / max(T, 1.0) < tol_T:
            return T_new, W0, it + 1, inner_iters

        T = T_new
        W0_guess = W0

    return T, W0_guess, max_outer, inner_iters

# ============================================================
# 10) RUN OVER S GRID AND PLOT T vs S
# ============================================================
S_min = 0.6 * S_ref_ft2
S_max = 1.4 * S_ref_ft2
N = 30
S_grid = np.linspace(S_min, S_max, N)

T_guess = 15000.0
tol_W = 1e-4
tol_T = 1e-4
max_inner = 200
max_outer = 100

print("=== Iteration settings (REQUIRED) ===")
print(f"T_guess   = {T_guess:.1f} lbf")
print(f"tol_W     = {tol_W:.1e}")
print(f"tol_T     = {tol_T:.1e}")
print(f"max_inner = {max_inner}")
print(f"max_outer = {max_outer}\n")

print("=== Key inputs ===")
print(f"W_crew [lb]        = {W_crew:.0f}")
print(f"W_payload_case [lb]= {W_payload_case:.0f}")
print(f"W_engine [lb]      = {W_engine:.0f}")
print(f"CD0_total          = {CD0_total:.5f}")
print(f"Dash condition     = Mach {M_dash} @ {alt_ft:.0f} ft")
print(f"Mission condition  = Mach {M_mission} @ {alt_ft:.0f} ft (for fuel fraction)\n")

T_vals, W_vals, outer_its, inner_its = [], [], [], []

for S in S_grid:
    T_sol, W_sol, out_it, in_it = solve_thrust_outer(
        S, T_guess=T_guess, tol_T=tol_T, tol_W=tol_W,
        max_outer=max_outer, max_inner=max_inner
    )
    T_vals.append(T_sol)
    W_vals.append(W_sol)
    outer_its.append(out_it)
    inner_its.append(in_it)

T_vals = np.array(T_vals)
W_vals = np.array(W_vals)

plt.figure()
plt.plot(S_grid, T_vals, linewidth=2, label="Dash Mach 1.6 @ 30kft")
plt.xlabel("Wing Area S (ft^2)")
plt.ylabel("Required Thrust T (lbf)")
plt.title("T vs S Constraint Curve (nested W and T convergence)")
plt.grid(True)
plt.legend()
plt.show()

print("Sample points (S, T, W0):")
for idx in np.linspace(0, len(S_grid)-1, 5, dtype=int):
    print(f"S={S_grid[idx]:7.1f} ft^2  ->  T={T_vals[idx]:10.0f} lbf,  W0={W_vals[idx]:9.0f} lb")
