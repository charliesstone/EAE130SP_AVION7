# ============================================================
# MODIFIED DAPCA IV COST MODEL (Corrected)
# - Uses real PW F135 engine cost
# - Uses per-aircraft avionics cost
# - Separates RDT&E and production costs
# ============================================================

import math

# -----------------------------
# 0) Known / assumptions
# -----------------------------
We = 32948.0          # empty weight [lb]
M_max = 1.6
V_max_kt = 942.9

Q_total = 500
Q_5yr = 500
Q = min(Q_total, Q_5yr)

FTA = 5               # flight-test aircraft

# Propulsion selection
N_engines_per_aircraft = 1
engine_unit_cost = 20_400_000   # PW F135 [$]

# Avionics assumption
avionics_unit_cost = 8_000_000  # [$ per aircraft]

# Inflation factor
inflation_2012_to_2026 = 1.420


# -----------------------------
# 1) Hourly rate fits
# -----------------------------
year = 2026

R_E = 2.576 * year - 5058
R_T = 2.883 * year - 5666
R_M = 2.316 * year - 4552
R_Q = 2.60  * year - 5112


# -----------------------------
# 2) DAPCA labor hours
# -----------------------------
H_E = 4.86 * (We ** 0.777) * (V_max_kt ** 0.894) * (Q ** 0.163)
H_T = 5.99 * (We ** 0.777) * (V_max_kt ** 0.696) * (Q ** 0.263)
H_M = 7.37 * (We ** 0.820) * (V_max_kt ** 0.484) * (Q ** 0.641)

H_Q = 0.133 * H_M


# -----------------------------
# 3) Convert hours to cost
# -----------------------------
Cost_engineering = H_E * R_E
Cost_tooling = H_T * R_T
Cost_manufacturing = H_M * R_M
Cost_qc = H_Q * R_Q


# -----------------------------
# 4) 2012$ cost terms
# -----------------------------
C_D_2012 = 91.3 * (We ** 0.630) * (V_max_kt ** 1.300)
C_F_2012 = 2498.0 * (We ** 0.325) * (V_max_kt ** 0.822) * (FTA ** 1.210)
C_Mat_2012 = 22.1 * (We ** 0.921) * (V_max_kt ** 0.621) * (Q ** 0.799)

# Inflate to 2026
C_D = C_D_2012 * inflation_2012_to_2026
C_F = C_F_2012 * inflation_2012_to_2026
C_Mat = C_Mat_2012 * inflation_2012_to_2026


# -----------------------------
# 5) Engine procurement
# -----------------------------
N_eng_total = Q_total * N_engines_per_aircraft
C_eng_total = engine_unit_cost * N_eng_total


# -----------------------------
# 6) Avionics procurement
# -----------------------------
C_avionics_total = avionics_unit_cost * Q_total


# -----------------------------
# 7) Cost breakdown
# -----------------------------

# Nonrecurring (RDT&E-like)
RDTandE_cost = (
    Cost_engineering
    + Cost_tooling
    + C_D
    + C_F
)

# Recurring production
production_cost_total = (
    Cost_manufacturing
    + Cost_qc
    + C_Mat
    + C_eng_total
    + C_avionics_total
)

# Total program cost
total_program_cost = RDTandE_cost + production_cost_total


# -----------------------------
# 8) Per-aircraft metrics
# -----------------------------
flyaway_cost = production_cost_total / Q_total
avg_program_cost = total_program_cost / Q_total


# -----------------------------
# 9) Print results
# -----------------------------
print("=== MODIFIED DAPCA IV COST MODEL ===\n")

print("--- Aircraft Parameters ---")
print(f"Empty Weight (We)               = {We:,.0f} lb")
print(f"Max Speed                       = {V_max_kt:,.1f} kt")
print(f"Production Quantity             = {Q_total}")
print()

print("--- Labor Hours ---")
print(f"Engineering Hours               = {H_E:,.0f}")
print(f"Tooling Hours                   = {H_T:,.0f}")
print(f"Manufacturing Hours             = {H_M:,.0f}")
print(f"QC Hours                        = {H_Q:,.0f}")
print()

print("--- Labor Cost ---")
print(f"Engineering Cost                = ${Cost_engineering:,.0f}")
print(f"Tooling Cost                    = ${Cost_tooling:,.0f}")
print(f"Manufacturing Cost              = ${Cost_manufacturing:,.0f}")
print(f"QC Cost                         = ${Cost_qc:,.0f}")
print()

print("--- Additional Cost Terms ---")
print(f"Development Support             = ${C_D:,.0f}")
print(f"Flight Test                     = ${C_F:,.0f}")
print(f"Manufacturing Materials         = ${C_Mat:,.0f}")
print()

print("--- Propulsion ---")
print(f"Engines per Aircraft            = {N_engines_per_aircraft}")
print(f"F135 Unit Cost                  = ${engine_unit_cost:,.0f}")
print(f"Total Engine Procurement        = ${C_eng_total:,.0f}")
print()

print("--- Avionics ---")
print(f"Avionics per Aircraft           = ${avionics_unit_cost:,.0f}")
print(f"Total Avionics Cost             = ${C_avionics_total:,.0f}")
print()

print("=== COST SUMMARY ===")
print(f"RDT&E Cost                      = ${RDTandE_cost:,.0f}")
print(f"Production Cost Total           = ${production_cost_total:,.0f}")
print(f"Total Program Cost              = ${total_program_cost:,.0f}")
print()

print(f"Flyaway Cost per Aircraft       = ${flyaway_cost:,.0f}")
print(f"Avg Program Cost per Aircraft   = ${avg_program_cost:,.0f}")