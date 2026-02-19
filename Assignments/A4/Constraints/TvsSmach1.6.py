# 1.6 mach constraint 
import numpy as np
import math
import matplotlib.pyplot as plt

# ============================================================
# 0) CONSTANTS / FIXED INPUTS (
# ============================================================
kg_to_lb = 2.2046226218

# --- Crew + payload  ---
W_crew = 1 * 95.0 * kg_to_lb  # one pilot incl gear (lb)

W_avionics = 2500.0
W_AIM9X = 190.0
W_MK83_JDAM = 1050.0

stores_install_fraction = 0.06
def add_installation(W_payload_total):
    weapons_only = max(W_payload_total - W_avionics, 0.0)
    return W_payload_total + stores_install_fraction * weapons_only

# pick ONE payload case (strike shown) 
W_payload = add_installation(W_avionics + 4*W_MK83_JDAM + 2*W_AIM9X)

# --- Aero inputs ---
AR = 3.5
CD0_clean = 0.0190     
e_clean = 0.825
k_induced = 1.0 / (math.pi * AR * e_clean)

# --- Dash condition  ---
M_dash = 1.6
alt_ft = 30000.0

# Fuel fraction inputs 
R_nmi  = 4000.0
E_hr   = 0.5
c_tsfc = 0.75
reserve_factor = 1.06

segment_fracs = {"Takeoff":0.990, "Climb":0.980, "Descent":0.990, "Landing":0.995}
W_small = 1.0
for f in segment_fracs.values():
    W_small *= f

# Representative cruise speed used in Breguet 
V_ms = 548.0
V_kt = V_ms * 1.9438444924

# Fighter empty-weight correlation 
A = 2.392
C = -0.13

# ============================================================
# 1) ISA atmosphere (ENGLISH) to get rho and speed of sound
# ============================================================
def isa_atm_english(alt_ft):
    """
    Returns: T [R], a [ft/s], rho [slug/ft^3]
    """
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
V_dash_ft_s = M_dash * a_ft_s
q_dash = 0.5 * rho * V_dash_ft_s**2  # dynamic pressure [lbf/ft^2]

# ============================================================
# 2) Engine-weight coupling so W = W(S,T) 
#    Set to 1 engine 
# ============================================================
n_eng = 1

def engine_weight_from_thrust(T_total):
    """
    Empirical engine weight vs thrust (tutorial-style).
    Not fighter-perfect, but creates W(S,T) coupling for the nested solver.
    """
    T_total = float(max(T_total, 1.0))
    T0 = T_total / n_eng

    W_eng_dry = 0.521 * (T0**0.9)
    W_eng_oil = 0.082 * (T0**0.65)
    W_eng_rev = 0.034 * T0
    W_eng_control = 0.26 * (T0**0.5)
    W_eng_start = 9.33 * ((W_eng_dry/1000) ** 1.078)
    W_eng = W_eng_dry + W_eng_oil + W_eng_rev + W_eng_control + W_eng_start

    install_factor = 1.3
    return n_eng * install_factor * W_eng  # total installed engine weight [lb]

# ============================================================
# 3) Fuel fraction — UPDATED inside inner loop using current L/D from WS and polar
# ============================================================
def fuel_fraction_total_from_WS(W0, S):
    """
    Updates fuel fraction using L/D computed from current W0 and S
    at the DASH dynamic pressure (q_dash) and polar CD = CD0 + k CL^2.
    """
    W0 = float(max(W0, 1.0))
    S  = float(max(S, 1.0))

    WS = W0 / S
    CL = WS / q_dash
    CD = CD0_clean + k_induced * CL**2
    LD = CL / max(CD, 1e-9)

    # Breguet cruise + loiter 
    Wf_Wi_cruise = math.exp(-R_nmi * c_tsfc / (V_kt * LD))
    Wf_Wi_loiter = math.exp(-E_hr  * c_tsfc / (LD))

    W_end_W0 = W_small * Wf_Wi_cruise * Wf_Wi_loiter
    fuel_frac_mission = 1.0 - W_end_W0
    fuel_frac_total = reserve_factor * fuel_frac_mission

    # guardrails
    return max(0.01, min(fuel_frac_total, 0.70))

# ============================================================
# 4) CONSTRAINT FUNCTION: DASH (T/W required as function of W/S)
#    T/W = (q*CD0)/(W/S) + (k*(W/S))/q
# ============================================================
def TW_req_dash(WS):
    WS = float(max(WS, 1e-9))
    return (q_dash * CD0_clean) / WS + (k_induced * WS) / q_dash

# ============================================================
# 5) INNER LOOP: converge weight W0 for fixed (S, T)
# ============================================================
def solve_weight_inner_loop(S, T_total, W0_guess=80000.0, tol_W=1e-6, max_iter_W=200):
    W0 = float(max(W0_guess, 1.0))
    hist = []

    for it in range(max_iter_W):
        W0 = float(max(W0, 1.0))

        # Update empty fraction from correlation
        We_W0 = A * (W0**C)

        # Update fuel fraction using current WS -> CL -> L/D
        Wf_W0 = fuel_fraction_total_from_WS(W0, S)

        # Engine coupling
        W_eng = engine_weight_from_thrust(T_total)

        denom = 1.0 - We_W0 - Wf_W0
        denom = float(max(denom, 0.08))  # guard

        W0_new = (W_payload + W_crew + W_eng) / denom
        hist.append(W0_new)

        rel = abs(W0_new - W0) / max(abs(W0_new), 1e-9)
        W0 = W0_new
        if rel < tol_W:
            return W0, True, it+1, np.array(hist), We_W0, Wf_W0, W_eng

    return W0, False, max_iter_W, np.array(hist), We_W0, Wf_W0, W_eng

# ============================================================
# 6) OUTER LOOP: converge thrust for DASH constraint at each S
# ============================================================
def solve_outer_loop_for_S_dash(S, T_guess=20000.0, W0_guess=80000.0,
                                tol_T=1e-4, max_iter_T=200, relax=1.0):
    T = float(max(T_guess, 1.0))
    T_hist = []
    last_W_hist = None
    last_W0 = None

    for itT in range(max_iter_T):
        W0, wconv, itW, W_hist, WeW0, WfW0, W_eng = solve_weight_inner_loop(
            S, T, W0_guess=W0_guess, tol_W=1e-6, max_iter_W=200
        )

        WS = W0 / S
        TW = TW_req_dash(WS)
        T_req = TW * W0

        T_hist.append(T)
        relT = abs(T_req - T) / max(abs(T), 1e-9)

        last_W_hist = W_hist
        last_W0 = W0

        if relT < tol_T:
            return T_req, W0, True, itT+1, np.array(T_hist), last_W_hist

        T = (1-relax)*T + relax*T_req
        W0_guess = W0  # warm-start inner loop next outer iteration

    return T, last_W0, False, max_iter_T, np.array(T_hist), last_W_hist

# ============================================================
# 7) RUN: Build T vs S curve (assignment requirement)
# ============================================================
S_grid = np.linspace(350, 850, 30)  # 20–40 points is fine
T_curve = []
W_curve = []
iters_outer = []

# Reported settings (required)
T_guess = 20000.0
tol_T = 1e-4
tol_W = 1e-6
max_iter_T = 200
max_iter_W = 200
relax = 1.0

for S in S_grid:
    T_sol, W_sol, conv, itT, Thist, Whist = solve_outer_loop_for_S_dash(
        S, T_guess=T_guess, W0_guess=80000.0,
        tol_T=tol_T, max_iter_T=max_iter_T, relax=relax
    )
    T_curve.append(T_sol)
    W_curve.append(W_sol)
    iters_outer.append(itT)

T_curve = np.array(T_curve)
W_curve = np.array(W_curve)

plt.figure(figsize=(12,7))
plt.plot(S_grid, T_curve, marker="o", label=f"Dash Mach {M_dash} @ {alt_ft:,.0f} ft")
plt.xlabel("Wing Area S (ft²)")
plt.ylabel("Total Thrust T (lbf)")
plt.title("Converged T vs S — Dash Constraint (nested W and T convergence)")
plt.grid(True)
plt.legend()
plt.show()


S_demo = float(S_grid[len(S_grid)//2])
T_sol, W_sol, conv, itT, Thist, Whist = solve_outer_loop_for_S_dash(
    S_demo, T_guess=T_guess, W0_guess=80000.0, tol_T=1e-6, max_iter_T=max_iter_T, relax=relax
)

plt.figure(figsize=(12,6))
plt.plot(Thist, marker="o")
plt.xlabel("Outer iteration k")
plt.ylabel("T guess (lbf)")
plt.title(f"Outer loop convergence (T) — dash constraint at S = {S_demo:.0f} ft²")
plt.grid(True)
plt.show()

plt.figure(figsize=(12,6))
plt.plot(Whist, marker="o")
plt.xlabel("Inner iteration k")
plt.ylabel("W0 estimate (lb)")
plt.title(f"Inner loop convergence (W0) at S = {S_demo:.0f} ft² (final converged T)")
plt.grid(True)
plt.show()

print("=== Iteration settings (copy into report) ===")
print(f"S grid: {S_grid[0]:.0f} to {S_grid[-1]:.0f} ft^2, N = {len(S_grid)}")
print(f"T_guess   = {T_guess:.0f} lbf")
print(f"tol_T_rel = {tol_T:.1e} (outer)")
print(f"tol_W_rel = {tol_W:.1e} (inner)")
print(f"max_iter_T = {max_iter_T}, max_iter_W = {max_iter_W}, relax = {relax}")
print()
print("=== Dash condition + aero used ===")
print(f"Dash: Mach {M_dash} @ {alt_ft:.0f} ft")
print(f"q_dash = {q_dash:.1f} lbf/ft^2")
print(f"CD0_clean = {CD0_clean:.4f}, AR={AR:.2f}, e={e_clean:.3f}, k={k_induced:.5f}")
print(f"n_eng = {n_eng} (single engine)")
print()
print("=== Demo point ===")
print(f"S_demo = {S_demo:.0f} ft^2 | converged={conv} | outer iters={itT} | W0={W_sol:,.0f} lb | T={T_sol:,.0f} lbf")
