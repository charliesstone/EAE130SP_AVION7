import numpy as np
import math
import matplotlib.pyplot as plt

# ============================================================
# 0) CONSTANTS / FIXED INPUTS (edit these to match your project)
# ============================================================
kg_to_lb = 2.2046226218

# --- Crew + payload (use your Code 1 values) ---
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

# --- Aero (use your Code 2/3 values) ---
AR = 3.5
CD0_clean = 0.0190
e_clean = 0.825
k_induced = 1.0 / (math.pi * AR * e_clean)

# --- Climb constraint parameters (from your Code 3 structure) ---
# You can tune these to match the class slide / metabook version you’re using.
ks = 3.4                 # V_climb ~ ks * V_stall
G  = 0.220               # climb gradient (ft/ft) A2 code 
tempoverinc = 1/0.8      # thrust lapse factor A2 code
maxcont2max = 1/0.94     # max continuous to max thrust factor A2 code

# Choose CLmax for climb segment (often CLmax_takeoff)
CLmax_climb = 1.7        # takeoff CLmax_T

# Fuel fraction inputs 
R_nmi  = 4000.0
E_hr   = 0.5
c_tsfc = 0.75
reserve_factor = 1.06

segment_fracs = {"Takeoff":0.990, "Climb":0.980, "Descent":0.990, "Landing":0.995}
W_small = 1.0
for f in segment_fracs.values():
    W_small *= f

# Use a representative cruise speed just to compute fuel fraction
# (If your class wants V tied to T/W or S, you can improve later)
V_ms = 548.0
V_kt = V_ms * 1.9438444924

# ============================================================
# 1) MODELS (fuel fraction, empty fraction, engine-weight coupling)
# ============================================================

# Fighter empty-weight correlation from your Code 1
A = 2.392
C = -0.13

# Add a thrust->engine weight coupling so W = W(S,T) (as in tutorial outer-loop idea)
n_eng = 2
def engine_weight_from_thrust(T_total):
    """
    Empirical engine weight vs thrust (tutorial-style).
    This isn't a fighter-perfect model; it’s here to create
    a realistic W(S,T) coupling for the nested solver.
    """
    T_total = float(max(T_total, 1.0))
    T0 = T_total / n_eng
    W_eng_dry = 0.521 * (T0**0.9)
    W_eng_oil = 0.082 * (T0**0.65)
    W_eng_rev = 0.034 * T0
    W_eng_control = 0.26 * (T0**0.5)
    W_eng_start = 9.33 * ((W_eng_dry/1000) ** 1.078)
    W_eng = W_eng_dry + W_eng_oil + W_eng_rev + W_eng_control + W_eng_start
    return n_eng * 1.3 * W_eng  # install factor

def fuel_fraction_total(W0, LD_eff=11.5*0.94):
    """
    Mission fuel fraction Wf/W0 (same structure as your Code 1).
    If you want to couple fuel to S, you can replace LD_eff
    with an L/D computed from CL(W,S) later.
    """
    Wf_Wi_cruise = math.exp(-R_nmi * c_tsfc / (V_kt * LD_eff))
    Wf_Wi_loiter = math.exp(-E_hr  * c_tsfc / (LD_eff))
    W_end_W0 = W_small * Wf_Wi_cruise * Wf_Wi_loiter
    fuel_frac_mission = 1.0 - W_end_W0
    return reserve_factor * fuel_frac_mission

# ============================================================
# 2) CONSTRAINT FUNCTION: CLIMB (T/W required)
# ============================================================
def TW_req_climb():
    """
    Your A2-style climb constraint:
    T/W = tempoverinc * maxcont2max * (ks^2*CD0/CLmax + k*CLmax/ks^2 + G)
    This is constant for given aero + CLmax + chosen ks/G/etc.
    """
    TW_gen = (ks**2 * CD0_clean)/(CLmax_climb) + (k_induced * CLmax_climb)/(ks**2) + G
    return tempoverinc * maxcont2max * TW_gen

TW_CLIMB = TW_req_climb()

# ============================================================
# 3) INNER LOOP: converge weight W0 for fixed (S, T)
# ============================================================
def solve_weight_inner_loop(S, T_total, W0_guess=80000.0, tol_W=1e-6, max_iter_W=200):
    W0 = float(max(W0_guess, 1.0))
    hist = []

    # fuel fraction (kept constant here, same as your Code 1 baseline)
    Wf_W0 = fuel_fraction_total(W0)

    for it in range(max_iter_W):
        W0 = float(max(W0, 1.0))
        We_W0 = A * (W0**C)

        # engine coupling
        W_eng = engine_weight_from_thrust(T_total)

        denom = 1.0 - We_W0 - Wf_W0
        # guard so iteration doesn't blow up if denom gets too small
        denom = float(max(denom, 0.08))

        W0_new = (W_payload + W_crew + W_eng) / denom
        hist.append(W0_new)

        rel = abs(W0_new - W0) / max(abs(W0_new), 1e-9)
        W0 = W0_new
        if rel < tol_W:
            return W0, True, it+1, np.array(hist), We_W0, Wf_W0, W_eng

    return W0, False, max_iter_W, np.array(hist), We_W0, Wf_W0, W_eng

# ============================================================
# 4) OUTER LOOP: converge thrust for CLIMB constraint at each S
# ============================================================
def solve_outer_loop_for_S_climb(S, T_guess=30000.0, W0_guess=80000.0,
                                 tol_T=1e-4, max_iter_T=200, relax=1.0):
    T = float(max(T_guess, 1.0))
    T_hist = []
    last_W_hist = None
    last_W0 = None

    for itT in range(max_iter_T):
        W0, wconv, itW, W_hist, WeW0, WfW0, W_eng = solve_weight_inner_loop(
            S, T, W0_guess=W0_guess, tol_W=1e-6, max_iter_W=200
        )

        # CLIMB constraint is constant T/W requirement (given your A2 form)
        T_req = TW_CLIMB * W0

        T_hist.append(T)
        relT = abs(T_req - T) / max(abs(T), 1e-9)

        last_W_hist = W_hist
        last_W0 = W0

        if relT < tol_T:
            return T_req, W0, True, itT+1, np.array(T_hist), last_W_hist

        T = (1-relax)*T + relax*T_req

    return T, last_W0, False, max_iter_T, np.array(T_hist), last_W_hist

# ============================================================
# 5) RUN: Build T vs S curve (as assignment asks)
# ============================================================
S_grid = np.linspace(350, 850, 30)  # 20–40 points
T_curve = []
W_curve = []
iters_outer = []

for S in S_grid:
    T_sol, W_sol, conv, itT, Thist, Whist = solve_outer_loop_for_S_climb(
        S, T_guess=30000.0, W0_guess=80000.0, tol_T=1e-4, max_iter_T=200, relax=1.0
    )
    T_curve.append(T_sol)
    W_curve.append(W_sol)
    iters_outer.append(itT)

T_curve = np.array(T_curve)
W_curve = np.array(W_curve)

# REQUIRED GRAPH: T vs S
plt.figure(figsize=(12,7))
plt.plot(S_grid, T_curve, marker="o")
plt.xlabel("Wing Area S (ft²)")
plt.ylabel("Total Thrust T (lbf)")
plt.title("Converged T vs S — Climb Constraint")
plt.grid(True)
plt.show()

# OPTIONAL: show convergence at one S (helps in writeup)
S_demo = float(S_grid[len(S_grid)//2])
T_sol, W_sol, conv, itT, Thist, Whist = solve_outer_loop_for_S_climb(
    S_demo, T_guess=30000.0, W0_guess=80000.0, tol_T=1e-6, max_iter_T=200, relax=1.0
)

plt.figure(figsize=(12,6))
plt.plot(Thist, marker="o")
plt.xlabel("Outer iteration k")
plt.ylabel("T guess (lbf)")
plt.title(f"Outer loop convergence (T) — climb constraint at S = {S_demo:.0f} ft²")
plt.grid(True)
plt.show()

plt.figure(figsize=(12,6))
plt.plot(Whist, marker="o")
plt.xlabel("Inner iteration k")
plt.ylabel("W0 estimate (lb)")
plt.title(f"Inner loop convergence (W0) at S = {S_demo:.0f} ft² (final converged T)")
plt.grid(True)
plt.show()

print("=== Iteration settings (report these) ===")
print(f"S grid: {S_grid[0]:.0f} to {S_grid[-1]:.0f} ft^2, N = {len(S_grid)}")
print(f"Climb constraint T/W (constant) = {TW_CLIMB:.4f}")
print("Outer loop: tol_T_rel = 1e-4, max_iter_T = 200, relax = 1.0")
print("Inner loop: tol_W_rel = 1e-6, max_iter_W = 200")
print()
print("=== Demo point ===")
print(f"S_demo = {S_demo:.0f} ft^2 | converged={conv} | outer iters={itT} | W0={W_sol:,.0f} lb | T={T_sol:,.0f} lbf")
