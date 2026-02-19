"""
(Single-Engine Fighter)
Constraint curve: CLIMB (gray line from team constraint diagram) -> constant T/W

WHAT THIS SCRIPT DOES:
1) Generates a T vs S plot with one constraint curve clearly labeled (Climb).
2) Demonstrates a nested solver:
   - Inner loop: converges TOGW W0 = W0(S, T) using a fighter empty-weight build-up model.
   - Outer loop: converges thrust T such that T = (T/W)_climb * W0.
3) Prints iteration settings: T_guess, tol_W, tol_T, max_iter_W, max_iter_T.

Model assumptions :
- Cd0 = 0.019
- Fuel fraction Wf/W0 = 0.306
- OpenVSP CompGeom baseline areas (ft^2): S_ref=573, S_ht=191.6, S_vt=92.3, S_fus_wet=288
- Baseline scaling (geometric similarity): HT/VT/fuselage areas scale with S/S_ref
- Fighter weight table multipliers + fractions
- Roskam engine weight regression (engine weight from thrust)
- Payload uses governing mission (max of AA vs Strike): avionics + weapons + 6% install allowance
"""

import numpy as np
import matplotlib.pyplot as plt


# =========================
# 1) FIXED INPUTS
# =========================
CD0 = 0.019
e = 0.8
AR = 3.5
k_induced = 1.0 / (np.pi * e * AR)

# Fuel fraction (total) 
Wf_W0 = 0.306

# Single pilot weight 
kg_to_lb = 2.2046226218
pilot_mass_kg = 95.0
W_crew = pilot_mass_kg * kg_to_lb  # lb


# =========================
# 1b) PAYLOAD (GOVERNING CASE) 
# Payload = RFP avionics (2500 lb) + weapons + 6% install allowance
# =========================
W_avionics = 2500.0
stores_install_fraction = 0.06

# Air-to-Air: 6x AIM-120C, 2x AIM-9X
W_AIM120 = 350.0
W_AIM9X  = 190.0
weapons_AA = 6 * W_AIM120 + 2 * W_AIM9X
W_payload_AA = W_avionics + weapons_AA * (1.0 + stores_install_fraction)

# Strike: 4x MK-83 JDAM, 2x AIM-9X
W_MK83_JDAM = 1050.0
weapons_STRIKE = 4 * W_MK83_JDAM + 2 * W_AIM9X
W_payload_STRIKE = W_avionics + weapons_STRIKE * (1.0 + stores_install_fraction)

# Governing payload 
W_payload = max(W_payload_AA, W_payload_STRIKE)
gov_case = "Air-to-Air" if W_payload_AA >= W_payload_STRIKE else "Strike"


# =========================
# 2) BASELINE GEOMETRY ( ft^2)
# =========================
S_ref_base = 573.0    # wing reference area (ft^2)
S_ht_base  = 191.6    # H Stabs wet area (ft^2)
S_vt_base  = 92.3     # V Stab wet area (ft^2)
S_fus_base = 288.0    # fuselage wetted area (ft^2)


# =========================
# 3) FIGHTER WEIGHT TABLE CONSTANTS
# =========================
WING_LBFT2 = 9.0
HT_LBFT2   = 4.0
VT_LBFT2   = 5.3
FUS_LBFT2  = 4.8

GEAR_NAVY_FRAC = 0.045
ALL_ELSE_FRAC  = 0.17
INSTALLED_ENG_FACTOR = 1.3


# =========================
# 4) ROSKAM ENGINE WEIGHT REGRESSION (single engine)
# =========================
def engine_weight_roskam(T0_lbf: float) -> float:
    """Engine weight (lb) from max sea-level static thrust T0 (lbf)."""
    T0 = max(float(T0_lbf), 1.0)
    W_eng_dry   = 0.521 * T0**0.9
    W_eng_oil   = 0.082 * T0**0.65
    W_eng_rev   = 0.034 * T0
    W_eng_ctrl  = 0.26  * T0**0.5
    W_eng_start = 9.33 * (W_eng_dry / 1000.0) ** 1.078
    return W_eng_dry + W_eng_oil + W_eng_rev + W_eng_ctrl + W_eng_start


# =========================
# 5) BASELINE SCALING GEOMETRY MODEL
# =========================
def scaled_geometry_from_S(S_wing: float):
    """
    Baseline scaling (geometric similarity):
    as wing area S changes, HT/VT/fuselage areas scale by S/S_ref_base.
    """
    S = float(S_wing)
    scale = S / S_ref_base
    S_ht = scale * S_ht_base
    S_vt = scale * S_vt_base
    S_fus = scale * S_fus_base
    return S_ht, S_vt, S_fus


# =========================
# 6) EMPTY WEIGHT BUILD-UP: We = We(S, T, W0)
# =========================
def empty_weight_build_up(W0: float, S_wing: float, T0_lbf: float) -> float:
    """
    Fighter empty weight using:
    - area-based components (wing/HT/VT/fuselage)
    - fractions of TOGW (gear, all-else)
    - installed engine weight from Roskam regression (function of T0)
    """
    S_ht, S_vt, S_wet_fus = scaled_geometry_from_S(S_wing)

    W_wing = WING_LBFT2 * S_wing
    W_ht   = HT_LBFT2   * S_ht
    W_vt   = VT_LBFT2   * S_vt
    W_fus  = FUS_LBFT2  * S_wet_fus

    W_gear  = GEAR_NAVY_FRAC * W0
    W_other = ALL_ELSE_FRAC  * W0

    W_engine = engine_weight_roskam(T0_lbf)
    W_eng_inst = INSTALLED_ENG_FACTOR * W_engine

    return W_wing + W_ht + W_vt + W_fus + W_gear + W_other + W_eng_inst


# =========================
# 7) INNER LOOP: CONVERGE W0 FOR FIXED (S, T)
# =========================
def inner_loop_weight(
    S_wing: float,
    T0_lbf: float,
    W0_init: float = 80000.0,
    tol_W: float = 1e-6,
    max_iter_W: int = 200,
):
    """
    INNER WEIGHT LOOP (converged when |W0_new - W0|/W0 < tol_W):
      W0_new = We(S, T, W0) + W_crew + W_payload + Wf
      Wf     = (Wf/W0) * W0
    """
    W0 = float(W0_init)

    for it in range(1, max_iter_W + 1):
        We = empty_weight_build_up(W0, S_wing, T0_lbf)
        Wf = Wf_W0 * W0
        W0_new = We + W_crew + W_payload + Wf

        rel_err = abs(W0_new - W0) / max(abs(W0_new), 1e-9)
        W0 = W0_new

        if rel_err < tol_W:
            return W0, True, it, rel_err

    return W0, False, max_iter_W, rel_err


# =========================
# 8) CLIMB CONSTRAINT (GRAY LINE): CONSTANT T/W
# =========================
def climb_TW_constant(
    Cd0: float,
    k: float,
    CLmax_climb: float = 1.7,
    ks: float = 3.4,
    G: float = 0.220,
    tempoverinc: float = 1/0.8,
    maxcont2max: float = 1/0.94
) -> float:
    """
    Climb constraint from team constraint diagram:
      TW_gen = (ks^2 * Cd0)/CL + (k*CL)/(ks^2) + G
      TW = tempoverinc * maxcont2max * TW_gen
    """
    TW_gen = (ks**2 * Cd0) / CLmax_climb + (k * CLmax_climb) / (ks**2) + G
    return tempoverinc * maxcont2max * TW_gen


# =========================
# 9) OUTER LOOP: CONVERGE T FOR EACH S (CLIMB CONSTRAINT)
# =========================
def outer_loop_T_vs_S_climb(
    S_grid,
    T_guess: float = 22000.0,
    W0_guess: float = 80000.0,
    tol_T: float = 1e-3,
    max_iter_T: int = 100,
    relax: float = 1.0,
    tol_W: float = 1e-6,
    max_iter_W: int = 200,
):
    """
    OUTER THRUST LOOP (converged when |T_req - T|/T < tol_T):
      1) Call inner loop to converge W0(S, T)
      2) Compute required thrust from climb: T_req = (T/W)_climb * W0
      3) Update T until converged
    """
    TW_req = climb_TW_constant(CD0, k_induced)

    T_curve = []
    W0_curve = []
    itT_curve = []
    itW_curve = []

    for S in S_grid:
        T = float(T_guess)

        for itT in range(1, max_iter_T + 1):
            # (1) Inner loop: converge weight for current (S, T)
            W0, wconv, itW, errW = inner_loop_weight(
                S_wing=S,
                T0_lbf=T,
                W0_init=W0_guess,
                tol_W=tol_W,
                max_iter_W=max_iter_W
            )

            # (2) Outer update from climb constraint
            T_req = TW_req * W0

            # (3) Check outer convergence
            rel_err_T = abs(T_req - T) / max(abs(T), 1e-9)
            if rel_err_T < tol_T:
                T = T_req
                break

            # Update thrust (use relax < 1.0 if outer loop ever oscillates)
            T = (1 - relax) * T + relax * T_req

        T_curve.append(T)
        W0_curve.append(W0)
        itT_curve.append(itT)
        itW_curve.append(itW)

    return np.array(T_curve), np.array(W0_curve), np.array(itT_curve), np.array(itW_curve), TW_req


# =========================
# 10) RUN + PLOT
# =========================
if __name__ == "__main__":
    # Wing area sweep (ft^2)
    S_grid = np.linspace(350, 750, 30)

    # Iteration settings (required by rubric)
    T_guess = 22000.0
    tol_W = 1e-6
    tol_T = 1e-3
    max_iter_W = 200
    max_iter_T = 100

    print("\n=== MODEL INPUTS USED ===")
    print("Single engine, single pilot")
    print(f"Cd0 = {CD0}")
    print(f"Wf/W0 = {Wf_W0}")
    print(f"W_crew = {W_crew:.1f} lb (95 kg pilot+gear)")

    print("\n=== PAYLOAD  ===")
    print(f"W_avionics = {W_avionics:.1f} lb")
    print(f"AA payload     = {W_payload_AA:.1f} lb")
    print(f"Strike payload = {W_payload_STRIKE:.1f} lb")
    print(f"--> Governing payload used = {W_payload:.1f} lb ({gov_case})")

    print("\n=== BASELINE GEOMETRY (OpenVSP) ===")
    print(f"S_ref_base = {S_ref_base} ft^2")
    print(f"S_ht_base  = {S_ht_base} ft^2")
    print(f"S_vt_base  = {S_vt_base} ft^2")
    print(f"S_fus_base = {S_fus_base} ft^2 (fuselage wetted)")

    print("\n=== ITERATION SETTINGS (REPORT THESE) ===")
    print(f"T_guess     = {T_guess:.1f} lbf")
    print(f"tol_W       = {tol_W}   (inner loop)")
    print(f"tol_T       = {tol_T}   (outer loop)")
    print(f"max_iter_W  = {max_iter_W}")
    print(f"max_iter_T  = {max_iter_T}")

    T_curve, W0_curve, itT, itW, TW_climb = outer_loop_T_vs_S_climb(
        S_grid=S_grid,
        T_guess=T_guess,
        W0_guess=80000.0,
        tol_T=tol_T,
        max_iter_T=max_iter_T,
        relax=1.0,
        tol_W=tol_W,
        max_iter_W=max_iter_W
    )

    print(f"\nCLIMB constraint used: T/W = {TW_climb:.3f}")

    mid = len(S_grid) // 2
    print("\n=== EXAMPLE CONVERGED POINT ===")
    print(f"S = {S_grid[mid]:.1f} ft^2")
    print(f"W0 = {W0_curve[mid]:.0f} lb")
    print(f"T  = {T_curve[mid]:.0f} lbf")
    print(f"Outer its = {itT[mid]}, Inner its = {itW[mid]}")

    # T vs S plot (required)
    plt.figure(figsize=(10, 6))
    plt.plot(S_grid, T_curve, marker="o", label="Climb constraint")
    plt.xlabel("Wing Area S (ft²)")
    plt.ylabel("Converged Total Thrust T (lbf)")
    plt.title("T vs S — Climb Constraint (Nested Solver, Baseline-Scaled Fighter)")
    plt.grid(True)
    plt.legend()
    plt.show()

    # Optional W0 vs S (useful sanity check)
    plt.figure(figsize=(10, 6))
    plt.plot(S_grid, W0_curve, marker="o")
    plt.xlabel("Wing Area S (ft²)")
    plt.ylabel("Converged TOGW W0 (lb)")
    plt.title("W0 vs S — Converged Weight from Inner Loop")
    plt.grid(True)
    plt.show()
