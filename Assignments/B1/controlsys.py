import math

# ============================================
# Control System Weight (Raymer)
# ============================================

# Inputs
M = 2.0                  # Mach number
N_en = 1.0               # number of engines
N_c = 1.0                # number of crew
L_ec = 15.45             # ft (engine to cockpit distance)
N_s = 4.0                # number of control systems

# Control surface areas (ft^2)
S_csw = 105.33
S_vt = 281.28
Sr_over_Svt = 0.045
S_r = Sr_over_Svt * S_vt

# Total control surface area
S_cs = S_csw + S_r

# -----------------------------
# Raymer Equations
# -----------------------------

# Engine controls weight
W_engine_controls = 10.5 * (N_en ** 1.008) * (L_ec ** 0.222)

# Flight controls weight
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
# Output
# -----------------------------
print(f"Total control system weight = {W_control_system:.2f} lb")

