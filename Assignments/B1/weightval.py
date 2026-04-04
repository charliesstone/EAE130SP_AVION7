import math


# Empennage + Control System Weight Estimation
# Raymer fighter/attack equations
# ============================================================

# -----------------------------
# 1) DESIGN INPUTS
# -----------------------------
W_dg = 36700.0          # design gross weight, lb
M = 0.85             # design/cruise Mach number
n_limit = 7.0           # limit load factor, g
N_z = 1.5 * n_limit     # ultimate load factor

# -----------------------------
# 2) CONFIGURATION FLAGS
# -----------------------------
# Horizontal tail 
H_t_over_H_v = 0.0     

# Horizontal tail is not a rolling tail
K_rht = 1.0             # 1.047 for rolling tail, 1.0 otherwise

# -----------------------------
# 3) GEOMETRY FROM OPENVSP
# -----------------------------

# Wing
S_w = 400.0             # main wing area, ft^2
X_wing = 18.553         # wing X location, ft

# Horizontal tail
S_ht = 140.25339        # horizontal tail area, ft^2
B_h = 21.0              # horizontal tail span, ft
X_ht = 35.173           # horizontal tail X location, ft

# Vertical tail
S_vt = 140.64069        # vertical tail area, ft^2
A_vt = 2.62705          # vertical tail aspect ratio
X_vt = 32.961           # vertical tail X location, ft

# Fuselage
F_w = 5.0               # fuselage width at H-tail intersection, ft
L_ec = 48.28            # engine controls length, ft (estimated as fuselage length)

# -----------------------------
# 4) DERIVED TAIL QUANTITIES
# -----------------------------

# Tail arm approximation:
# Using difference in X-location between wing and tail
# Raymer wants quarter-MAC to quarter-MAC distance; this is an approximation.
L_t = X_vt - X_wing     # ft

# Vertical tail taper ratio from VSP sections
root_chord_vt = 11.48294
tip_chord_vt = 2.73402
lambda_vt = tip_chord_vt / root_chord_vt

# Vertical tail quarter chord sweep approximation:
# area weighted average of the three VStab section sweeps
vt_sec_areas = [20.06702, 49.06481, 1.18851]           # ft^2
vt_sec_sweeps_deg = [45.0, 51.85714, 51.85714]         # deg

Lambda_vt_deg = sum(a * s for a, s in zip(vt_sec_areas, vt_sec_sweeps_deg)) / sum(vt_sec_areas)
Lambda_vt_rad = math.radians(Lambda_vt_deg)

# Rudder area approximation from VSP sub-surfaces
# lower rudder: 0.42 -> 0.50, chord ratio 0.25
# upper rudder: 0.50 -> 0.60, chord ratio 0.25
Sr_lower = (0.50 - 0.42) * 0.25 * S_vt
Sr_upper = (0.60 - 0.50) * 0.25 * S_vt
S_r = Sr_lower + Sr_upper

# -----------------------------
# 5) CONTROL-SURFACE AREA FOR FLIGHT CONTROLS
# -----------------------------
# Using VSP sub-surface extents and chord ratios

# Main wing control surfaces
S_aileron = (0.725 - 0.60) * 0.25 * S_w
S_flaperon = (0.60 - 0.50) * 0.25 * S_w
S_inboard_flap = (0.50 - 0.35) * 0.25 * S_w
S_le_slat = (0.75 - 0.55) * 0.15 * S_w

# Horizontal tail elevators
S_elevator_inboard = (0.40 - 0.30) * 0.25 * S_ht
S_elevator_outboard = (0.60 - 0.40) * 0.25 * S_ht
S_elevator_total = S_elevator_inboard + S_elevator_outboard

# Vertical tail rudders
S_rudder_total = S_r

# Total control surface area
# Including primary movable surfaces and high-lift devices with actuators/linkages
S_cs = (
    S_aileron
    + S_flaperon
    + S_inboard_flap
    + S_le_slat
    + S_elevator_total
    + S_rudder_total
)

# -----------------------------
# 6) OTHER CONTROL-SYSTEM INPUTS
# -----------------------------
N_en = 1.0              # number of engines
N_c = 1.0               # number of crew 
N_s = 4.0               # number of flight control systems (assumed: pitch, roll, yaw, high-lift)

# -----------------------------
# 7) RAYMER EQUATIONS
# -----------------------------

# Eq. 15.2 - Horizontal tail weight
W_ht = (
    3.316
    * (1.0 + F_w / B_h) ** (-2.0)
    * ((W_dg * N_z) / 1000.0) ** 0.260
    * S_ht ** 0.806
)

# Eq. 15.3 - Vertical tail weight
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

# Total empennage
W_empennage = W_ht + W_vt

# Eq. 15.14 - Engine controls weight
W_engine_controls = 10.5 * (N_en ** 1.008) * (L_ec ** 0.222)

# Eq. 15.17 - Flight controls weight
W_flight_controls = (
    36.28
    * M ** 0.003
    * S_cs ** 0.489
    * N_s ** 0.484
    * N_c ** 0.127
)

# Total control system weight
W_control_system = W_engine_controls + W_flight_controls

# -----------------------------
# 8) PRINT RESULTS
# -----------------------------
print("===========================================")
print("EMPENNAGE + CONTROL SYSTEM WEIGHT RESULTS")
print("===========================================")

print(f"W_dg                  = {W_dg:.2f} lb")
print(f"M                     = {M:.3f}")
print(f"n_limit               = {n_limit:.2f}")
print(f"N_z                   = {N_z:.2f}")
print()

print("---- Derived Inputs ----")
print(f"L_t                   = {L_t:.3f} ft")
print(f"lambda_vt             = {lambda_vt:.4f}")
print(f"Lambda_vt             = {Lambda_vt_deg:.3f} deg")
print(f"S_r                   = {S_r:.3f} ft^2")
print(f"S_cs                  = {S_cs:.3f} ft^2")
print()

print("---- Empennage ----")
print(f"Horizontal tail weight W_ht    = {W_ht:.3f} lb")
print(f"Vertical tail weight   W_vt    = {W_vt:.3f} lb")
print(f"Total empennage weight         = {W_empennage:.3f} lb")
print()

print("---- Control System ----")
print(f"Engine controls weight         = {W_engine_controls:.3f} lb")
print(f"Flight controls weight         = {W_flight_controls:.3f} lb")
print(f"Total control system weight    = {W_control_system:.3f} lb")
print()

print("---- Component Areas Used in S_cs ----")
print(f"Aileron area                   = {S_aileron:.3f} ft^2")
print(f"Flaperon area                  = {S_flaperon:.3f} ft^2")
print(f"Inboard flap area              = {S_inboard_flap:.3f} ft^2")
print(f"LE slat area                   = {S_le_slat:.3f} ft^2")
print(f"Elevator total area            = {S_elevator_total:.3f} ft^2")
print(f"Rudder total area              = {S_rudder_total:.3f} ft^2")
print("===========================================")