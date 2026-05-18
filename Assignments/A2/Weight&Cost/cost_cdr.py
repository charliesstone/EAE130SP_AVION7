# ============================================================
# MODIFIED DAPCA IV COST MODEL (Corrected)
# - Uses PW F119 engine cost from 2012$ range
# - Inflates engine cost to 2026$
# - Uses per-aircraft avionics cost
# - Separates RDT&E and production costs
# ============================================================

import math

# -----------------------------
# 0) Known / assumptions
# -----------------------------
We = 21373          # empty weight [lb]
M_max = 1.6
V_max_kt = 942.9

Q_total = 500
Q_5yr = 500
Q = min(Q_total, Q_5yr)

FTA = 5               # flight-test aircraft

# Inflation factor
inflation_2012_to_2026 = 1.420

# Propulsion selection: PW F119
N_engines_per_aircraft = 1

# Historical F119 unit cost range in 2012 dollars
engine_unit_cost_2012_low = 9_000_000
engine_unit_cost_2012_high = 10_000_000

# Inflate to 2026 dollars
engine_unit_cost_low = engine_unit_cost_2012_low * inflation_2012_to_2026
engine_unit_cost_high = engine_unit_cost_2012_high * inflation_2012_to_2026

# Use midpoint for baseline estimate
engine_unit_cost = 0.5 * (engine_unit_cost_low + engine_unit_cost_high)

# Avionics assumption
avionics_unit_cost = 8_000_000  # [$ per aircraft]

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

# Inflate to 2026 dollars
C_D = C_D_2012 * inflation_2012_to_2026
C_F = C_F_2012 * inflation_2012_to_2026
C_Mat = C_Mat_2012 * inflation_2012_to_2026

# -----------------------------
# 5) Engine procurement
# -----------------------------
N_eng_total = Q_total * N_engines_per_aircraft
C_eng_total = engine_unit_cost * N_eng_total

# Optional low/high sensitivity bounds
C_eng_total_low = engine_unit_cost_low * N_eng_total
C_eng_total_high = engine_unit_cost_high * N_eng_total

# -----------------------------
# 6) Avionics procurement
# -----------------------------
C_avionics_total = avionics_unit_cost * Q_total

# -----------------------------
# 7) Cost breakdown
# -----------------------------
RDTandE_cost = (
    Cost_engineering
    + Cost_tooling
    + C_D
    + C_F
)

production_cost_total = (
    Cost_manufacturing
    + Cost_qc
    + C_Mat
    + C_eng_total
    + C_avionics_total
)

total_program_cost = RDTandE_cost + production_cost_total

# Sensitivity totals
production_cost_total_low = (
    Cost_manufacturing
    + Cost_qc
    + C_Mat
    + C_eng_total_low
    + C_avionics_total
)

production_cost_total_high = (
    Cost_manufacturing
    + Cost_qc
    + C_Mat
    + C_eng_total_high
    + C_avionics_total
)

total_program_cost_low = RDTandE_cost + production_cost_total_low
total_program_cost_high = RDTandE_cost + production_cost_total_high

# -----------------------------
# 8) Per-aircraft metrics
# -----------------------------
flyaway_cost = production_cost_total / Q_total
avg_program_cost = total_program_cost / Q_total

flyaway_cost_low = production_cost_total_low / Q_total
flyaway_cost_high = production_cost_total_high / Q_total

avg_program_cost_low = total_program_cost_low / Q_total
avg_program_cost_high = total_program_cost_high / Q_total

# -----------------------------
# 8.5) DIRECT OPERATING COST (DOC)
# -----------------------------
# Conceptual fighter DOC model ($/flight hour)

# ---- Fuel assumptions ----
fuel_burn_lb_per_hr = 18000      # conceptual combat average [lb/hr]
fuel_density_lb_per_gal = 6.7    # JP-8
fuel_cost_per_gal = 4.00         # 2026 conceptual assumption [$]

fuel_burn_gal_per_hr = fuel_burn_lb_per_hr / fuel_density_lb_per_gal
fuel_cost_per_hr = fuel_burn_gal_per_hr * fuel_cost_per_gal

# ---- Maintenance assumptions ----
# Single-engine naval fighter assumptions
engine_maintenance_per_hr = 9000     # engine inspections/overhaul reserve
airframe_maintenance_per_hr = 7000   # structure, landing gear, hydraulics, avionics upkeep
crew_ops_per_hr = 1500               # pilot support + consumables + servicing

DOC_per_flight_hour = (
    fuel_cost_per_hr
    + engine_maintenance_per_hr
    + airframe_maintenance_per_hr
    + crew_ops_per_hr
)

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
print(f"F119 Unit Cost (2012$ range)    = ${engine_unit_cost_2012_low:,.0f} to ${engine_unit_cost_2012_high:,.0f}")
print(f"F119 Unit Cost (2026$ range)    = ${engine_unit_cost_low:,.0f} to ${engine_unit_cost_high:,.0f}")
print(f"F119 Unit Cost (2026$ midpoint) = ${engine_unit_cost:,.0f}")
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

print()
print("=== DIRECT OPERATING COST (DOC) ===")
print(f"Fuel Burn Rate                  = {fuel_burn_lb_per_hr:,.0f} lb/hr")
print(f"Fuel Cost per Flight Hour       = ${fuel_cost_per_hr:,.0f}")
print(f"Engine Maintenance per Hour     = ${engine_maintenance_per_hr:,.0f}")
print(f"Airframe Maintenance per Hour   = ${airframe_maintenance_per_hr:,.0f}")
print(f"Crew / Ops per Hour             = ${crew_ops_per_hr:,.0f}")
print(f"Total DOC per Flight Hour       = ${DOC_per_flight_hour:,.0f}")

print(f"Flyaway Cost per Aircraft       = ${flyaway_cost:,.0f}")
print(f"Avg Program Cost per Aircraft   = ${avg_program_cost:,.0f}")
print()

print("=== ENGINE COST SENSITIVITY ===")
print(f"Flyaway Cost Range              = ${flyaway_cost_low:,.0f} to ${flyaway_cost_high:,.0f}")
print(f"Avg Program Cost Range          = ${avg_program_cost_low:,.0f} to ${avg_program_cost_high:,.0f}")