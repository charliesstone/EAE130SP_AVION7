# ============================================================
# Iterative T–S Sizing Solver
# Coupled Weight Model + Service Ceiling Constraint
# ============================================================

import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. Aerodynamic Parameters
# ============================================================

AR = 3.5
e = 0.8

S_wet = 2044.71        # ft^2
S_ref = 573.00         # ft^2
c_f = 0.0026

C_D_0 = c_f * (S_wet / S_ref)

# Service ceiling constraint
K = 1 / (np.pi * e * AR)
TW_ceiling = 2 * np.sqrt(K * C_D_0)

print("Zero-lift drag coefficient C_D0 =", C_D_0)
print("Ceiling T/W required =", TW_ceiling)

# ============================================================
# 2. Payload and Crew
# ============================================================

num_pilot = 1
num_crew = 0
num_passengers = 0

avg_wt_person = 95      # kg
avg_wt_luggage = 27     # kg

def kgs_to_lbs(weight_kg):
    return weight_kg * 2.20462

W_crew = kgs_to_lbs((num_pilot + num_crew) * (avg_wt_person + avg_wt_luggage))
W_payload = kgs_to_lbs(num_passengers * (avg_wt_person + avg_wt_luggage))

# ============================================================
# 3. Engine Weight Model
# ============================================================

def calculate_engine_weight(T_0):
    W_eng_dry = 0.521 * T_0**0.9
    W_eng_oil = 0.082 * T_0**0.65
    W_eng_rev = 0.034 * T_0
    W_eng_control = 0.26 * T_0**0.5
    W_eng_start = 9.33 * (W_eng_dry/1000) ** 1.078
    return W_eng_dry + W_eng_oil + W_eng_rev + W_eng_control + W_eng_start

# ============================================================
# 4. Empty Weight Model
# ============================================================

def calculate_empty_weight(S_wing, S_ht, S_vt, S_wet_fuselage,
                           TOGW, T_0, num_engines):

    W_wing = S_wing * 9
    W_ht = S_ht * 4
    W_vt = S_vt * 5.3
    W_fuselage = S_wet_fuselage * 4.8
    W_landing_gear = 0.033 * TOGW
    W_engines = calculate_engine_weight(T_0) * num_engines * 1.3
    W_all_else = 0.17 * TOGW

    return (W_wing + W_ht + W_vt +
            W_fuselage + W_landing_gear +
            W_engines + W_all_else)

# ============================================================
# 5. Fuel Fraction Model (Breguet)
# ============================================================

L_D_max = 11 * 0.94
R = 4000          # nmi
E = 0.5           # hr
c = 00.75         # lb/(lbf hr)
V = 548 * 1.94    # knots

def calculate_fuel_fraction():

    L_D = 0.94 * L_D_max

    W3_W2 = np.exp((-R * c) / (V * L_D))
    W4_W3 = np.exp((-E * c) / (L_D))

    W1_W0 = 0.970
    W2_W1 = 0.985
    W5_W4 = 0.995

    W5_W0 = W5_W4 * W4_W3 * W3_W2 * W2_W1 * W1_W0
    Wf_W0 = (1 - W5_W0) * 1.06

    return Wf_W0

# ============================================================
# 6. Inner Loop – Converged Weight Model
# ============================================================

def inner_loop_weight(TOGW_guess,
                      S_wing, S_ht, S_vt, S_wet_fuselage,
                      num_engines, W_crew, W_payload, T_0,
                      tol=1e-6, max_iter=200):

    for _ in range(max_iter):

        Wf_W0 = calculate_fuel_fraction()
        W_fuel = Wf_W0 * TOGW_guess

        W_empty = calculate_empty_weight(
            S_wing, S_ht, S_vt, S_wet_fuselage,
            TOGW_guess, T_0, num_engines
        )

        W0_new = W_empty + W_crew + W_payload + W_fuel

        if abs(W0_new - TOGW_guess) / W0_new < tol:
            return W0_new

        TOGW_guess = W0_new

    return TOGW_guess

# ============================================================
# 7. Outer Loop – Ceiling T–S Solver
# ============================================================

def outer_loop_TS_solver(S_grid,
                         TOGW_guess_init,
                         T_guess_init,
                         num_engines,
                         S_ht, S_vt, S_wet_fuselage):

    T_results = []
    W_results = []

    for S in S_grid:

        T_total = T_guess_init

        for _ in range(200):

            T_0 = T_total / num_engines

            W0 = inner_loop_weight(
                TOGW_guess_init,
                S, S_ht, S_vt, S_wet_fuselage,
                num_engines, W_crew, W_payload, T_0
            )

            T_required = TW_ceiling * W0

            if abs(T_required - T_total) / T_total < 1e-6:
                break

            T_total = T_required

        T_results.append(T_total)
        W_results.append(W0)

    return np.array(T_results), np.array(W_results)

# ============================================================
# 8. Run Solver
# ============================================================

S_ht = 191.55648728
S_vt = 92.259532089
S_wet_fuselage = 288.238328907
num_engines = 1

S_wing_grid = np.linspace(3000, 6000, 100)

T_curve, W_curve = outer_loop_TS_solver(
    S_wing_grid,
    TOGW_guess_init=500000,
    T_guess_init=150000,
    num_engines=num_engines,
    S_ht=S_ht,
    S_vt=S_vt,
    S_wet_fuselage=S_wet_fuselage
)

# ============================================================
# 9. Plot Results
# ============================================================

plt.figure(figsize=(12,8))
plt.plot(S_wing_grid, T_curve)
plt.xlabel("Wing Area S (ft^2)")
plt.ylabel("Total Thrust Required (lbf)")
plt.title("Iterative T–S Sizing Solver (Service Ceiling Constraint)")
plt.grid(True)
plt.show()
