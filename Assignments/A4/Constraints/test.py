import numpy as np
import matplotlib.pyplot as plt

# ===================== Setup =====================
AR = 3.5
s_ref = 573
g = 32.174

S_wet = 2044
c_f = 0.0026

def calculate_zero_lift_drag_coefficient(c_f, S_wet, s_ref):
    return c_f * (S_wet / s_ref)

C_D_0 = 0.01755
print("Zero-lift drag coefficient C_D_0:", C_D_0)

def calculate_induced_drag_coefficient(AR, e):
    return 1/(np.pi*AR*e)

# Config efficiencies
e_clean = 0.820
e_takeoff = 0.75
e_landing = 0.7



# ===================== CRUISE COEFFICIENTS (used to plot WS->TW) kept for possible addition of T/W vs W/S=====================
rho = 5.85e-4          # slugs/ft^3 (ISA @ 40,000 ft)
a   = 968.1            # ft/s (ISA @ 40,000 ft)
M   = 0.84
V = M * a              # ft/s

C_D_0_cruise = C_D_0
e_cruise = e_clean

def calculate_cruise_constraint_coefficients(rho, V, C_D_0, AR, e):
    q = 0.5 * rho * V**2
    coef_1 = q * C_D_0
    coef_2 = 1/(np.pi * AR * e * q)
    return coef_1, coef_2

coef_1_cruise_constraint, coef_2_cruise_constraint = calculate_cruise_constraint_coefficients(
    rho, V, C_D_0_cruise, AR, e_cruise
)

def TW_from_cruise_at_WS(WS):
    """Cruise constraint converted to TW as a function of WS."""
    return (coef_1_cruise_constraint / WS) + (coef_2_cruise_constraint * WS)
# ============================================================================


#  STALL EQUATIONS 
#   V_stall_takeoff = 205 ft/s, CLmax_takeoff = 1.7
#   V_stall_landing = 220 ft/s, CLmax_landing = 2.2


rho_SL = 23.77e-4  # slugs/ft^3 at sea level (you were using this)

def WS_stall_takeoff(rho_takeoff, Vstall_takeoff, CLmax_takeoff):
    """
    TAKEOFF STALL wing-loading limit:
        WS = 0.5 * rho_to * Vstall_to^2 * CLmax_to
    (Keep separate from landing because rho/safety factors often differ.)
    """
    return 0.5 * rho_takeoff * (Vstall_takeoff**2) * CLmax_takeoff

def WS_stall_landing(rho_landing, Vstall_landing, CLmax_landing):
    """
    LANDING STALL wing-loading limit:
        WS = 0.5 * rho_L * Vstall_L^2 * CLmax_L
    (Kept separate from takeoff by request.)
    """
    return 0.5 * rho_landing * (Vstall_landing**2) * CLmax_landing

# inputs for stall limits 
Vstall_takeoff = 205.0
CLmax_takeoff = 1.7

Vstall_landing = 220.0
CLmax_landing = 2.2

WS_takeoff_stall_val = WS_stall_takeoff(rho_SL, Vstall_takeoff, CLmax_takeoff)
WS_landing_stall_val = WS_stall_landing(rho_SL, Vstall_landing, CLmax_landing)

print(f"[TAKEOFF STALL] WS_stall = {WS_takeoff_stall_val:.2f} lb/ft^2")
print(f"[LANDING STALL] WS_stall = {WS_landing_stall_val:.2f} lb/ft^2")

# Convert WS into TW target
TW_req_takeoff_stall = TW_from_cruise_at_WS(WS_takeoff_stall_val)
TW_req_landing_stall = TW_from_cruise_at_WS(WS_landing_stall_val)

print(f"[TAKEOFF STALL] TW_req (cruise @ WS_stall) = {TW_req_takeoff_stall:.4f}")
print(f"[LANDING STALL] TW_req (cruise @ WS_stall) = {TW_req_landing_stall:.4f}")
# ============================================================================


# ===================== CLIMB COEFFICIENT=====================
N_eng = 1
k_s = 1.2
C_L_max_climb = 2.2
G = 0.08
e = 0.8

def calculate_climb_constraint_coefficient(N_eng, k_s, C_L_max, C_D_0, AR, e, G):
    return (1/0.8) * ((k_s**2) / C_L_max * C_D_0 + C_L_max / (np.pi * AR * e * k_s**2) + G)

coef_1_climb_constraint = calculate_climb_constraint_coefficient(
    N_eng, k_s, C_L_max_climb, C_D_0, AR, e, G
)
print("[CLIMB] TW_req =", coef_1_climb_constraint)
# ============================================================================


# ===================== WEIGHT =====================
num_pilot = 1
avg_wt_person = 200
W_payload = 2500

W_crew = num_pilot * avg_wt_person
W_payload = W_crew + W_payload

L_D_max = 9
R = 1000
E = 30 / 60
c = 0.52
V_knots = 291 * 1.94

S_ht = 0
S_vt = 74
S_wet_fuselage = 288
num_engines = 1

def calculate_engine_weight(T_0):
    W_eng_dry = 0.521 * T_0**0.9
    W_eng_oil = 0.082 * T_0**0.65
    W_eng_rev = 0.034 * T_0
    W_eng_control = 0.26 * T_0**0.5
    W_eng_start = 9.33 * (W_eng_dry/1000) ** 1.078
    return W_eng_dry + W_eng_oil + W_eng_rev + W_eng_control + W_eng_start

def calculate_empty_weight(S_wing, S_ht, S_vt, S_wet_fuselage, TOGW, T_0 , num_engines):
    W_wing = S_wing * 10
    W_ht = S_ht * 5.5
    W_vt = S_vt * 5.5
    W_fuselage = S_wet_fuselage * 5
    W_landing_gear = 0.043 * TOGW
    Engine_weight = calculate_engine_weight(T_0)
    W_engines = Engine_weight * num_engines * 1.3
    W_all_else = 0.17 * TOGW

    fighter_scale = 3.5
    W_empty = fighter_scale * (W_wing + W_ht + W_vt + W_fuselage) + W_landing_gear + W_engines + W_all_else
    return W_empty

def calculate_weight_fraction(L_D_max, R, E, c, V):
    L_D = 0.94 * L_D_max
    W3_W2 = np.exp((-R*c) / (V*L_D))  # cruise
    W4_W3 = np.exp((-E*c) / (L_D))    # loiter

    #segment fractions
    W1_W0 = 0.990
    W2_W1 = 0.980
    W5_W4 = 0.995

    W5_W0 = W5_W4 * W4_W3 * W3_W2 * W2_W1 * W1_W0
    return (1 - W5_W0) * 1.06

def inner_loop_weight(
    TOGW_guess,
    S_wing, S_ht, S_vt, S_wet_fuselage,
    num_engines, w_crew, w_payload, T_0,
    err=1e-6,
    max_iter=200
):
    delta = np.inf
    it = 0

    while delta > err and it < max_iter:
        Wf_W0 = calculate_weight_fraction(L_D_max, R, E, c, V_knots)
        W_fuel = Wf_W0 * TOGW_guess

        W_empty = calculate_empty_weight(
            S_wing, S_ht, S_vt, S_wet_fuselage,
            TOGW_guess, T_0, num_engines
        )

        W0_new = W_empty + w_crew + w_payload + W_fuel
        delta = abs(W0_new - TOGW_guess) / max(abs(W0_new), 1e-9)
        TOGW_guess = W0_new
        it += 1

    return TOGW_guess, (delta <= err), it
# ============================================================================


# ===================== OUTER LOOPS =====================
def outer_loop_thrust_stall(
    S_wing_grid,
    WS_stall_target,
    TW_req_stall_target,
    T_total_guess_init,
    num_engines,
    S_ht, S_vt, S_wet_fuselage,
    W_crew, W_payload,
    tol_T_rel=1e-6,
    max_iter_T=200,
    relax=1.0
):
    """
    Stall outer loop:
    - TOGW_guess_local = WS_stall_target * S
    - fixed TW_req_stall_target (computed from cruise at WS_stall)
    - Converges total thrust: T_req = TW_req * W0
    """
    T_total_converged = []
    W0_converged = []
    iter_counts = []

    for S_wing in S_wing_grid:
        T_total = T_total_guess_init
        TOGW_guess_local = WS_stall_target * S_wing

        for k in range(max_iter_T):
            # single-engine: per-engine thrust == total thrust
            T_0 = T_total / max(num_engines, 1)

            W0, wconv, it_w = inner_loop_weight(
                TOGW_guess_local,
                S_wing, S_ht, S_vt, S_wet_fuselage,
                num_engines, W_crew, W_payload, T_0
            )

            # ------------------ ADD YOUR CONSTRAINT LINE HERE ------------------
            TW_req = TW_req_stall_target
            # -------------------------------------------------------------------

            T_req = TW_req * W0

            if abs(T_req - T_total) / max(abs(T_total), 1e-9) < tol_T_rel:
                T_total = T_req
                break

            T_total = (1 - relax) * T_total + relax * T_req

        T_total_converged.append(T_total)
        W0_converged.append(W0)
        iter_counts.append(k+1)

    return np.array(T_total_converged), np.array(W0_converged), np.array(iter_counts)

def outer_loop_thrust_climb(
    S_wing_grid,
    TOGW_guess_init,
    T_total_guess_init,
    num_engines,
    S_ht, S_vt, S_wet_fuselage,
    W_crew, W_payload,
    coef_1_climb_constraint,
    tol_T_rel=1e-6,
    max_iter_T=200,
    relax=1.0
):
    """
    Climb outer loop:
    - Uses a constant TW_req = coef_1_climb_constraint
    """
    T_total_converged = []
    W0_converged = []
    iter_counts = []

    for S_wing in S_wing_grid:
        T_total = T_total_guess_init

        for k in range(max_iter_T):
            T_0 = T_total / max(num_engines, 1)

            W0, wconv, it_w = inner_loop_weight(
                TOGW_guess_init,
                S_wing, S_ht, S_vt, S_wet_fuselage,
                num_engines, W_crew, W_payload, T_0
            )

            # ------------------ ADD YOUR CONSTRAINT LINE HERE ------------------
            TW_req = coef_1_climb_constraint
            # -------------------------------------------------------------------

            T_req = TW_req * W0

            if abs(T_req - T_total) / max(abs(T_total), 1e-9) < tol_T_rel:
                T_total = T_req
                break

            T_total = (1 - relax) * T_total + relax * T_req

        T_total_converged.append(T_total)
        W0_converged.append(W0)
        iter_counts.append(k+1)

    return np.array(T_total_converged), np.array(W0_converged), np.array(iter_counts)
# ============================================================================


# ===================== run + plots =====================
S_wing_grid = np.linspace(300, 800, 50)
TOGW_guess_init = 55000
T_total_guess_init = 45000

# Takeoff stall
T_takeoff_stall, W_takeoff_stall, it_takeoff = outer_loop_thrust_stall(
    S_wing_grid=S_wing_grid,
    WS_stall_target=WS_takeoff_stall_val,
    TW_req_stall_target=TW_req_takeoff_stall,
    T_total_guess_init=T_total_guess_init,
    num_engines=num_engines,
    S_ht=S_ht, S_vt=S_vt, S_wet_fuselage=S_wet_fuselage,
    W_crew=W_crew, W_payload=W_payload
)

plt.figure(figsize=(16,9))
plt.title("Converged T vs S — Takeoff Stall Constraint")
plt.xlabel("Wing Area S (ft^2)")
plt.ylabel("Total Thrust T (lbf)")
plt.plot(S_wing_grid, T_takeoff_stall, marker='o', label="Takeoff stall sizing")
plt.grid(True)
plt.legend(loc="best")
plt.show()

# Landing stall
T_landing_stall, W_landing_stall, it_landing = outer_loop_thrust_stall(
    S_wing_grid=S_wing_grid,
    WS_stall_target=WS_landing_stall_val,
    TW_req_stall_target=TW_req_landing_stall,
    T_total_guess_init=T_total_guess_init,
    num_engines=num_engines,
    S_ht=S_ht, S_vt=S_vt, S_wet_fuselage=S_wet_fuselage,
    W_crew=W_crew, W_payload=W_payload
)

plt.figure(figsize=(16,9))
plt.title("Converged T vs S — Landing Stall Constraint")
plt.xlabel("Wing Area S (ft^2)")
plt.ylabel("Total Thrust T (lbf)")
plt.plot(S_wing_grid, T_landing_stall, marker='o', label="Landing stall sizing")
plt.grid(True)
plt.legend(loc="best")
plt.show()

# Climb
T_climb, W_climb, it_climb = outer_loop_thrust_climb(
    S_wing_grid=S_wing_grid,
    TOGW_guess_init=TOGW_guess_init,
    T_total_guess_init=T_total_guess_init,
    num_engines=num_engines,
    S_ht=S_ht, S_vt=S_vt, S_wet_fuselage=S_wet_fuselage,
    W_crew=W_crew, W_payload=W_payload,
    coef_1_climb_constraint=coef_1_climb_constraint
)

# Combined
plt.figure(figsize=(16,9))
plt.title("Converged T vs S — Combined Constraints (Takeoff Stall + Landing Stall + Climb)")
plt.xlabel("Wing Area S (ft^2)")
plt.ylabel("Total Thrust T (lbf)")
plt.plot(S_wing_grid, T_takeoff_stall, marker='o', label="Takeoff stall")
plt.plot(S_wing_grid, T_landing_stall, marker='o', label="Landing stall")
plt.plot(S_wing_grid, T_climb, marker='o', label="Climb")
plt.grid(True)
plt.legend(loc="best")
plt.show()
# ============================================================================