import math


W_dg_guess = 36700.0     # lb, current design gross-weight guess
N_z = 12.0               # ultimate load factor (8g limit => 12 ultimate)
M = 2.0

# Mission payloads
W_payload_A2A = 2382.0   # lb
W_payload_strike = 4372.0  # lb

# Crew
N_crew = 2
W_crew_each = 200.0
W_crew = N_crew * W_crew_each

# Wing and engine weights 
W_wing = 2847.0          # lb
W_eng = 5000.0           # lb

# Placeholder 
W_landing_gear = 0.0     # lb  <-- replace later


# FUSELAGE

def fuselage_weight(Kdwf, Wdg, Nz, L, D, W):
    return 0.499 * Kdwf * (Wdg ** 0.35) * (Nz ** 0.25) * (L ** 0.5) * (D ** 0.849) * (W ** 0.685)

Kdwf = 1.0
L = 40.3604
D = 5.5
W = 5.0
W_fuselage = fuselage_weight(Kdwf, W_dg_guess, N_z, L, D, W)


# EMPENNAGE + CONTROL

W_dg = W_dg_guess

# Horizontal tail
S_ht = 280.51
B_h = 42.0
F_w = 5.0

# Vertical tail
S_vt = 140.5
A_vt = 2.627
lambda_vt = 0.5066
Lambda_vt_deg = 52.0
Lambda_vt_rad = math.radians(Lambda_vt_deg)
H_t_over_H_v = 0.0
L_t = 12.408
K_rht = 1.0

# Rudder ratio and area
Sr_over_Svt = 0.172
S_r = Sr_over_Svt * S_vt

# Control surfaces
S_csw = 105.33
S_cs = S_csw + S_r

# Engine / crew / controls
N_en = 1.0
N_c = 2.0
L_ec = 15.45
N_s = 4.0



W_ht = (
    3.316
    * (1.0 + F_w / B_h) ** (-2.0)
    * ((W_dg * N_z) / 1000.0) ** 0.260
    * S_ht ** 0.806
)

W_vt = (
    0.452
    * K_rht
    * (1.0 + H_t_over_H_v) ** 0.5
    * (W_dg * N_z) ** 0.488
    * S_vt ** 0.718
    * M ** 0.341
    * L_t ** (-1.0)
    * (1.0 + S_r / S_vt) ** 0.348
    * A_vt ** 0.223
    * (1.0 + lambda_vt) ** 0.25
    * (math.cos(Lambda_vt_rad)) ** (-0.323)
)

W_empennage = W_ht + W_vt

W_engine_controls = 10.5 * (N_en ** 1.008) * (L_ec ** 0.222)


W_flight_controls = (
    36.28
    * M ** 0.003
    * S_cs ** 0.489
    * N_s ** 0.484
    * N_c ** 0.127
)

W_control_system = W_engine_controls + W_flight_controls

# air induuction 
K_vg = 1.62
K_d = 2.7
L_d = 16.53
L_s = 6.5
N_en = 1.0
D_e = 78.5 / 12.0

W_air_induction = 13.29 * K_vg * (L_d ** 0.643) * (K_d ** 0.182) * (N_en ** 1.498) * ((L_s / L_d) ** (-0.373)) * D_e

# INSTRUMENTS

def instruments_weight(N_en, N_t, N_ci):
    return 8.0 + 36.37 * (N_en ** 0.676) * (N_t ** 0.237) + 26.4 * ((1 + N_ci) ** 1.356)

N_t = 3
N_ci = 1.2  # pilot + backseater
W_inst = instruments_weight(N_en, N_t, N_ci)


# FUEL / OIL / ELECTRICAL / HYD / PNEU

V_i = 1600.0
V_t = 1640.0
V_p = 1600.0
L_a = 30.0
N_gen = N_en
K_mc = 1.45
R_kva = 130.0
SFC = 1.9
T = 33500.0

W_fuelSys = (
    7.45
    * (V_t ** 0.47)
    * (1 + V_i / V_t) ** (-0.095)
    * (1 + V_p / V_t)
    * (N_t ** 0.066)
    * (N_en ** 0.052)
    * (T * SFC / 1000) ** 0.249
)

W_oil = 37.82 * (N_en ** 1.023)  

W_pneumatic = 49.19 * ((N_en * W_eng / 1000.0) ** 0.541)

W_hydraulics = 0.001 * W_dg

W_electrical = (
    172.2
    * K_mc
    * (R_kva ** 0.152)
    * (N_c ** 0.1)
    * (L_a ** 0.1)
    * (N_gen ** 0.091)
)

W_systems_group = W_electrical + W_fuelSys + W_hydraulics + W_oil + W_pneumatic


# TAILPIPE + STARTER

D_e = 78.5 / 12.0   # ft
L_tp = 4.7          # ft
T_e = 33500.0        # lbf
W_tailpipe = 3.5 * D_e * L_tp * N_en
W_starter = 0.025 * (T_e**0.760) * (N_en**0.720)


# FIXED WEIGHT BEFORE FUEL FRACTION + PAYLOAD

W_fixed = (
    W_wing
    + W_eng
    + W_fuselage
    + W_empennage
    + W_control_system
    + W_inst
    + W_systems_group
    + W_tailpipe
    + W_starter
    + W_air_induction
)


# TOGW SOLVER WITH FUEL = 30% OF TOGW
# TOGW = (fixed + LG + crew + payload) / 0.70

def solve_togw(W_fixed, W_landing_gear, W_crew, W_payload):
    return (W_fixed + W_landing_gear + W_crew + W_payload) / 0.70

W_TOGW_A2A = solve_togw(W_fixed, W_landing_gear, W_crew, W_payload_A2A)
W_TOGW_strike = solve_togw(W_fixed, W_landing_gear, W_crew, W_payload_strike)

W_fuel_A2A = 0.30 * W_TOGW_A2A
W_fuel_strike = 0.30 * W_TOGW_strike

# 
# Results printout

print("COMPONENT WEIGHTS: -------------------")
print(f"Wing             = {W_wing:.2f} lb")
print(f"Engine           = {W_eng:.2f} lb")
print(f"Fuselage         = {W_fuselage:.2f} lb")
print(f"Empennage        = {W_empennage:.2f} lb")
print(f"Control system   = {W_control_system:.2f} lb")
print(f"Instruments      = {W_inst:.2f} lb")
print(f"Electrical       = {W_electrical:.2f} lb")
print(f"Hydraulics       = {W_hydraulics:.2f} lb")
print(f"Pneumatics        = {W_pneumatic:.2f} lb")
print(f"Oil              = {W_oil:.2f} lb")
print(f"Fuel system      = {W_fuelSys:.2f} lb")
print(f"Tailpipe         = {W_tailpipe:.2f} lb")
print(f"Starter           = {W_starter:.2f} lb")
print(f"Crew             = {W_crew:.2f} lb")
print(f"Landing gear     = {W_landing_gear:.2f} lb")
print(f"Air induction system weight = {W_air_induction:.2f} lb")
print()

print("MISSION WEIGHTS: -------")
print(f"A2A payload      = {W_payload_A2A:.2f} lb")
print(f"A2A TOGW         = {W_TOGW_A2A:.2f} lb")
print(f"A2A fuel weight  = {W_fuel_A2A:.2f} lb")
print()

print(f"Strike payload = {W_payload_strike:.2f} lb")
print(f"Strike TOGW    = {W_TOGW_strike:.2f} lb")
print(f"Strike fuel weight   = {W_fuel_strike:.2f} lb")