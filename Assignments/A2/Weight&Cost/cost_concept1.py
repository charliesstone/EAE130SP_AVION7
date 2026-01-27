# ============================================================
# A2 COST SCALING MODEL
# Cost estimated as a function of empty weight (We)
# Result form: Cost ~= (coefficient) * We
# ============================================================

import math

# ------------------------------------------------------------
# 0) INPUT FROM WEIGHT ESTIMATION
# ------------------------------------------------------------
We = 32948.0   # empty weight [lb] from your weight code

# ------------------------------------------------------------
# 1) Mach -> KTAS conversion (ISA atmosphere)
# ------------------------------------------------------------
def isa_temperature_K(alt_ft):
    T0 = 288.15      # sea-level temperature [K]
    L  = 0.0065      # lapse rate [K/m]
    h_m = alt_ft * 0.3048
    if h_m <= 11000:
        return T0 - L * h_m
    else:
        return 216.65

def mach_to_ktas(M, alt_ft):
    gamma = 1.4
    R = 287.05
    T = isa_temperature_K(alt_ft)
    a = math.sqrt(gamma * R * T)   # speed of sound [m/s]
    V_ms = M * a
    return V_ms * 1.94384449       # convert m/s -> kt

# Max speed assumption
M_max = 1.6
alt_ft = 30000
Vmax_ktas = mach_to_ktas(M_max, alt_ft)

# ------------------------------------------------------------
# 2) Program assumptions
# ------------------------------------------------------------
Q_total = 500     # total production quantity
Q_5yr   = 500     # units produced in 5 years
Q_proto = 5       # number of prototypes

# ------------------------------------------------------------
# 3) Configuration correction factors (from lecture)
# ------------------------------------------------------------
# Composite-heavy, tapered wing, complex flaps, pressurized cabin
F_cert  = 1.00
F_comp  = 2.00
F_taper = 0.95
F_cf    = 1.00
F_press = 1.03
F_hye   = 1.00

# ------------------------------------------------------------
# 4) CPI escalation (2012 -> ~2026 USD) 
# ------------------------------------------------------------
CPI_2012 = 229.6
CPI_dec2025 = 326.03
CPI = CPI_dec2025 / CPI_2012

# ------------------------------------------------------------
# 5) Labor rates extrapolated to 2026 (from lecture slide)
# ------------------------------------------------------------
year = 2026
R_ENG  = 2.576 * year - 5058     # engineering rate [$ / hr]
R_TOOL = 2.883 * year - 5666
R_MFG  = 2.316 * year - 4552

# ------------------------------------------------------------
# 6) Structural airframe weight approximation
# ------------------------------------------------------------
k_struct = 0.45                  # structure ~= 45% of We
W_airframe = k_struct * We       # [lb]

# ------------------------------------------------------------
# 7) Cost Estimation Relationships (CERs)
# ------------------------------------------------------------

# Engineering cost
C_ENG = (
    0.083 *
    (W_airframe ** 0.791) *
    (Vmax_ktas ** 1.521) *
    (Q_5yr ** 0.183) *
    F_cert * F_cf * F_comp * F_press * F_hye *
    R_ENG * CPI
)

# Tooling cost
C_TOOL = (
    2.1036 *
    (W_airframe ** 0.764) *
    (Vmax_ktas ** 0.899) *
    (Q_5yr ** 0.178) *
    (Q_total ** 0.066) *
    F_taper * F_cf * F_comp * F_press * F_hye *
    R_TOOL * CPI
)

# Manufacturing cost
C_MFG = (
    20.2588 *
    (W_airframe ** 0.740) *
    (Vmax_ktas ** 0.543) *
    (Q_total ** 0.524) *
    F_cert * F_cf * F_comp * F_hye *
    R_MFG * CPI
)

# Development cost
C_DEV = (
    0.06458 *
    (W_airframe ** 0.873) *
    (Vmax_ktas ** 1.890) *
    (Q_proto ** 0.346) *
    F_cert * F_cf * F_comp * F_press * F_hye *
    CPI
)

# Flight test cost
C_FT = (
    0.009646 *
    (W_airframe ** 1.160) *
    (Vmax_ktas ** 1.372) *
    (Q_proto ** 1.281) *
    F_cert * F_hye *
    CPI
)

# ------------------------------------------------------------
# 8) Cost rollups
# ------------------------------------------------------------
RDT_E = C_ENG + C_DEV + C_FT
unit_cost = (C_TOOL + C_MFG) / Q_total

# Linearized "cost per We" form (nice for report text)
RDT_E_per_We = RDT_E / We
unit_cost_per_We = unit_cost / We

# ------------------------------------------------------------
# 9) Output (ASCII-safe)
# ------------------------------------------------------------
print("=== A2 COST ESTIMATION RESULTS ===")
print(f"Empty weight We           = {We:,.0f} lb")
print(f"Max speed                 = Mach {M_max} @ {alt_ft:,} ft")
print(f"Max speed (KTAS)          = {Vmax_ktas:,.1f}")
print(f"CPI factor (2026/2012)    = {CPI:.3f}")
print()

print(f"Engineering cost          = ${C_ENG:,.0f}")
print(f"Development cost          = ${C_DEV:,.0f}")
print(f"Flight test cost          = ${C_FT:,.0f}")
print(f"Total RDT&E               = ${RDT_E:,.0f}")
print()

print(f"Tooling cost (total)      = ${C_TOOL:,.0f}")
print(f"Manufacturing cost total  = ${C_MFG:,.0f}")
print(f"Unit production cost      = ${unit_cost:,.0f}")
print()

