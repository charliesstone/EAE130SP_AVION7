# ============================================================
# Inputs:
#   We [lb], V [kt], Q_total, Q_5yr, FTA (flight-test aircraft),
#   N_engines_per_aircraft, engine Tmax [lbf], T_turbine_inlet [degR],
#   Cavionics_2012 [$], inflation_factor (2012 -> 2026),
#   hourly rate fits (2026) for Engineering/Tooling/Mfg/QC
#
# Outputs:
#   Total program cost (RDT&E + flyaway) and per-aircraft average
# ============================================================

import math

# -----------------------------
# 0) Known / assumptions
# -----------------------------
We = 32948.0          # [lb] empty weight from your weight code
M_max = 1.6           # engine max Mach number (use aircraft max Mach if that’s your assumption)
V_max_kt = 942.9      # [kt] (you already computed Mach 1.6 @ 30kft -> ~942.9 kt)

Q_total = 500         # total production quantity
Q_5yr = 500           # number produced in five years
Q = min(Q_total, Q_5yr)  # definition in screenshot: "lesser of production quantity or number produced in five years"

FTA = 5               # flight-test aircraft (typical 2–6); in screenshot called FTA
N_engines_per_aircraft = 2

# Engine parameters needed for Eq (18.8) (fps form)
# NOTE: These are REQUIRED to compute C_eng. Use your engine sizing / comparable engine.
T_max_lbf = 26950.0         # [lbf] engine maximum thrust 
T_turbine_inlet_degR = 3500.0  # [degR] turbine inlet temp 

# Avionics cost term (Eq 18.9). This is NOT avionics weight.
# You must assume/estimate a dollar value (in 2012$), or set to 0 for now.
Cavionics_2012 = 30000000        # [2012$] PLACEHOLDER

# Inflation factor for the terms that are in 2012$ (CD, CF, CM, Ceng, Cavionics)
# Your earlier CPI ratio was ~1.42; use your team’s chosen 2012->2026 factor.
inflation_2012_to_2026 = 1.420

# -----------------------------
# 1) Hourly rate fits (from your lecture slide)
# -----------------------------
year = 2026
R_E = 2.576 * year - 5058   # Engineering rate [$ / hr]
R_T = 2.883 * year - 5666   # Tooling rate [$ / hr]
R_M = 2.316 * year - 4552   # Manufacturing rate [$ / hr]
R_Q = 2.60  * year - 5112   # QC rate [$ / hr]  (from the slide box: QC R_QC = 2.60y - 5112)

# -----------------------------
# 2) DAPCA labor HOURS (Eqs 18.1–18.4, fps form)
# -----------------------------
H_E = 4.86 * (We ** 0.777) * (V_max_kt ** 0.894) * (Q ** 0.163)          # engineering hours
H_T = 5.99 * (We ** 0.777) * (V_max_kt ** 0.696) * (Q ** 0.263)          # tooling hours
H_M = 7.37 * (We ** 0.820) * (V_max_kt ** 0.484) * (Q ** 0.641)          # manufacturing hours

# QC hours: use "otherwise" line (not cargo airplane)
H_Q = 0.133 * H_M

# Convert hours -> costs in current dollars (per screenshot text)
Cost_labor_current = H_E * R_E + H_T * R_T + H_M * R_M + H_Q * R_Q

# -----------------------------
# 3) 2012$ cost terms (Eqs 18.5–18.8, fps form) -> inflate to 2026$
# -----------------------------
# Development support cost (2012$)
C_D_2012 = 91.3 * (We ** 0.630) * (V_max_kt ** 1.300)

# Flight test cost (2012$)
C_F_2012 = 2498.0 * (We ** 0.325) * (V_max_kt ** 0.822) * (FTA ** 1.210)

# Manufacturing materials cost (2012$)
C_Mat_2012 = 22.1 * (We ** 0.921) * (V_max_kt ** 0.621) * (Q ** 0.799)

# Engine production cost (2012$) per engine (Eq 18.8, fps form)
C_eng_2012_per_engine = 3112.0 * (0.043 * T_max_lbf + 243.25 * M_max + 0.969 * T_turbine_inlet_degR - 2228.0)

# Total engines produced = Q_total * engines/aircraft
N_eng_total = Q_total * N_engines_per_aircraft
C_eng_total_2012 = C_eng_2012_per_engine * N_eng_total

# Inflate all 2012$ terms to 2026$
C_D = C_D_2012 * inflation_2012_to_2026
C_F = C_F_2012 * inflation_2012_to_2026
C_Mat = C_Mat_2012 * inflation_2012_to_2026
C_eng_total = C_eng_total_2012 * inflation_2012_to_2026
Cavionics = Cavionics_2012 * inflation_2012_to_2026

# -----------------------------
# 4) Total cost rollup (Eq 18.9)
# -----------------------------
total_program_cost = (
    Cost_labor_current
    + C_D + C_F + C_Mat
    + C_eng_total
    + Cavionics
)

avg_cost_per_aircraft = total_program_cost / Q_total

# -----------------------------
# 5) Print results
# -----------------------------
print("=== MODIFIED DAPCA IV RESULTS (fps form) ===")
print(f"We [lb]                 = {We:,.0f}")
print(f"V (max) [kt]            = {V_max_kt:,.1f}")
print(f"Q_total                 = {Q_total}")
print(f"Q_5yr                   = {Q_5yr}")
print(f"Q = min(Q_total,Q_5yr)  = {Q}")
print(f"FTA                     = {FTA}")
print(f"N engines / aircraft    = {N_engines_per_aircraft}")
print(f"Inflation (2012->2026)  = {inflation_2012_to_2026:.3f}")
print()

print("--- Labor hours (hr) ---")
print(f"H_E (eng)  = {H_E:,.0f}")
print(f"H_T (tool) = {H_T:,.0f}")
print(f"H_M (mfg)  = {H_M:,.0f}")
print(f"H_Q (QC)   = {H_Q:,.0f}")
print()

print("--- Labor cost (current $) ---")
print(f"Labor cost (HE*RE + HT*RT + HM*RM + HQ*RQ) = ${Cost_labor_current:,.0f}")
print()

print("--- 2012$ terms inflated to 2026$ ---")
print(f"C_D (dev support)       = ${C_D:,.0f}")
print(f"C_F (flight test)       = ${C_F:,.0f}")
print(f"C_M (materials)         = ${C_Mat:,.0f}")
print(f"C_eng (total engines)   = ${C_eng_total:,.0f}")
print(f"C_avionics              = ${Cavionics:,.0f}")
print()

print("=== TOTAL (Eq 18.9) ===")
print(f"Total program cost (RDT&E + flyaway) = ${total_program_cost:,.0f}")
print(f"Average cost per aircraft            = ${avg_cost_per_aircraft:,.0f}")
