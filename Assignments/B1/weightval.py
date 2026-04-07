import math

# ============================================
# Raymer Fighter/Attack Weight Estimation
# Empennage + Control System
# ============================================


W_dg = 36700.0          # lb
N_z = 12.0              # ultimate load factor
M = 2.0                 # design Mach number

# Horizontal tail
S_ht = 280.51           # ft^2, total both sides
B_h = 42.0              # ft
F_w = 5.0               # ft

# Vertical tail
S_vt = 281.28           # ft^2
A_vt = 2.627
lambda_vt = 0.238
Lambda_vt_deg = 52.0
Lambda_vt_rad = math.radians(Lambda_vt_deg)
t_c_root = 0.10        

# Tail config
H_t_over_H_v = 0.0      # not T-tail
L_t = 12.408            # ft -xvt-xwing
K_rht = 1.0            

# Rudder
Sr_over_Svt = 0.172
S_r = Sr_over_Svt * S_vt

# Control surfaces
S_aileron = 28.15       # ft^2
S_flaperon = 27.18      # ft^2
S_flap = 25.47          # ft^2
S_slat = 24.53          # ft^2
S_csw = 105.33          # ft^2

# Engine / crew
N_en = 1.0
N_c = 2.0
L_ec = 15.45            # ft, x eng-x pilot 
N_s = 4.0               # assumed flight-control systems


S_cs = S_csw + S_r

# -----------------------------
# 3) RAYMER EQUATIONS
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

# Total control system
W_control_system = W_engine_controls + W_flight_controls

# -----------------------------
# 4) PRINT RESULTS
# -----------------------------
print("===========================================")
print("RAYMER FIGHTER/ATTACK WEIGHT RESULTS")
print("===========================================")

print(f"W_dg                  = {W_dg:.2f} lb")
print(f"N_z                   = {N_z:.2f}")
print(f"M                     = {M:.3f}")
print()

print("---- Inputs Used ----")
print(f"S_ht                  = {S_ht:.3f} ft^2")
print(f"B_h                   = {B_h:.3f} ft")
print(f"F_w                   = {F_w:.3f} ft")
print(f"S_vt                  = {S_vt:.3f} ft^2")
print(f"A_vt                  = {A_vt:.4f}")
print(f"lambda_vt             = {lambda_vt:.4f}")
print(f"Lambda_vt             = {Lambda_vt_deg:.3f} deg")
print(f"L_t                   = {L_t:.3f} ft")
print(f"S_r                   = {S_r:.3f} ft^2")
print(f"S_csw                 = {S_csw:.3f} ft^2")
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
print("===========================================")
