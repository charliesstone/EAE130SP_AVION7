# Preliminary weight estimate (F/A-18E/F remodel to RFP)
# Uses fuel-fraction method + fighter empty-weight correlation + OpenVSP drag/wetted assumptions
import math

# -----------------------------
# 0) Constants / unit conversions
# -----------------------------
kg_to_lb = 2.2046226218
lb_to_kg = 1.0 / kg_to_lb

# -----------------------------
# 1) Crew + Payload Inputs (ONE PILOT, NO PASSENGERS)
# -----------------------------
# Crew
n_pilots = 1
pilot_mass_kg = 95.0  # major assumption: pilot + gear (edit if you want)
W_crew = n_pilots * pilot_mass_kg * kg_to_lb  # [lb]

# Payload (edit these to match your RFP mission case)
# RFP says avionics/sensors weight = 2,500 lb internal
W_avionics = 2500.0  # [lb]
W_engine = 3830

# Air-to-Air mission: 6x AIM-120C, 2x AIM-9X
W_AIM120 = 350  # [lb] 
W_AIM9X  = 190   # [lb] 
W_payload_AA = W_avionics + 6*W_AIM120 + 2*W_AIM9X

# -- Strike mission (RFP): 4x MK-83 JDAM, 2x AIM-9X
W_MK83_JDAM = 1050  # [lb] 
W_payload_STRIKE = W_avionics + 4*W_MK83_JDAM + 2*W_AIM9X

# Optional: add pylons/racks/pods/tankage as a simple % of external stores
stores_install_fraction = 0.06  # 6% of (weapons only); major assumption
def add_installation(W_payload_total):
    weapons_only = max(W_payload_total - W_avionics, 0.0)
    return W_payload_total + stores_install_fraction * weapons_only

W_payload_AA = add_installation(W_payload_AA)
W_payload_STRIKE = add_installation(W_payload_STRIKE)

print("=== Crew + Payload Summary ===")
print(f"W_crew [lb]              = {W_crew:,.0f}")
print(f"W_payload_AA [lb]        = {W_payload_AA:,.0f} (includes avionics + install allowance)")
print(f"W_payload_STRIKE [lb]    = {W_payload_STRIKE:,.0f} (includes avionics + install allowance)")
print()

# 
# 2) Fuel Fractions
# 
R_nmi     = 4000
E_hr      = 0.5
c_tsfc    = 0.75
LD_cruise = 11.5 * 0.94
V_ms      = 548
V_kt      = V_ms * 1.9438444924  # nmi/hr

# Breguet cruise: Wf/Wi = exp(-R*c / (V*(L/D)))
Wf_Wi_cruise = math.exp(-R_nmi * c_tsfc / (V_kt * LD_cruise))

# Breguet loiter: Wf/Wi = exp(-E*c / (L/D))
Wf_Wi_loiter = math.exp(-E_hr * c_tsfc / LD_cruise)

# Small segment fractions (edit if your class uses different tabulated values)
segment_fracs = {
    "Takeoff": 0.990,
    "Climb":   0.980,
    "Descent": 0.990,
    "Landing": 0.995
}

W_end_W0 = 1.0
for _, frac in segment_fracs.items():
    W_end_W0 *= frac

W_end_W0 *= Wf_Wi_cruise
W_end_W0 *= Wf_Wi_loiter

fuel_frac_mission = 1.0 - W_end_W0
reserve_factor    = 1.06
fuel_frac_total   = reserve_factor * fuel_frac_mission  # Wf/W0

print("=== Fuel Fraction Summary ===")
print(f"Cruise Wf/Wi             = {Wf_Wi_cruise:.4f}")
print(f"Loiter Wf/Wi             = {Wf_Wi_loiter:.4f}")
print(f"End-of-mission W_end/W0  = {W_end_W0:.4f}")
print(f"Fuel fraction (mission)  = {fuel_frac_mission:.4f}")
print(f"Fuel fraction (total)    = {fuel_frac_total:.4f}")
print()

# -----------------------------
# 3) TOGW Iteration
# -----------------------------
# Empty-weight fraction We/W0 = A * W0^C
A = 2.392
C = -0.13

def iterate_W0(W_payload, W_crew, fuel_frac, W0_guess=80000.0, err=1e-6, max_iter=200):
    W0 = float(W0_guess)
    for i in range(max_iter):
        We_W0 = A * (W0 ** C)
        denom = 1.0 - fuel_frac - We_W0
        #if denom <= 0:
            #raise ValueError(
                #f"Denominator <= 0. Check fuel fraction or A,C. "
                #f"We/W0={We_W0:.3f}, Wf/W0={fuel_frac:.3f}"
            #)
        W0_new = (W_payload + W_crew) / denom
        delta = abs(W0_new - W0) / abs(W0_new)
        W0 = W0_new
        if delta < err:
            return W0, We_W0, i+1, delta
    return W0, A * (W0 ** C), max_iter, delta

def solve_case(case_name, W_payload_case, W0_guess):
    W0, We_W0, iters, delta = iterate_W0(W_payload_case, W_crew, fuel_frac_total, W0_guess=W0_guess)
    We = We_W0 * W0
    Wf = fuel_frac_total * W0
    return {
        "name": case_name,
        "W0": W0 + W_engine,
        "We": We + W_engine,
        "Wf": Wf,
        "WeW0": We_W0,
        "WfW0": fuel_frac_total,
        "iters": iters
    }

aa = solve_case("Air-to-Air", W_payload_AA, W0_guess=75000.0)
st = solve_case("Strike",    W_payload_STRIKE, W0_guess=85000.0)

# Governing case (heavier W0)
gov = aa if aa["W0"] >= st["W0"] else st

print("=== TOGW Results ===")
for r in [aa, st]:
    print(f"{r['name']}:")
    print(f"  W0 (TOGW) [lb]         = {r['W0']:,.0f}")
    print(f"  We (empty) [lb]        = {r['We']:,.0f}")
    print(f"  Wf (fuel) [lb]         = {r['Wf']:,.0f}")
    print(f"  We/W0                  = {r['WeW0']:.4f}")
    print(f"  Wf/W0                  = {r['WfW0']:.4f}")
    print(f"  Converged in           = {r['iters']} iters")
print()
print(f"Governing (max TOGW) case: {gov['name']} with W0 = {gov['W0']:,.0f} lb")
print()

# 
# 4) OpenVSP assumed drag & wetted-area 
# 
CD0_total = 0.00539


# wetted area from OpenVSP 
S_wet_total_ft2 = 2044.71

# ref wing area from OpenVSP 
S_ref_ft2 = 573.0

wetted_ratio = S_wet_total_ft2 / S_ref_ft2  # Swet/Sref


# 5) RFP checks

# RFP constraint: Maximum takeoff gross weight shall not be > 90,000 lb
W0_ref_rfp_max = 90000.0

# Also compute an "empty weight at the RFP cap" based on the same correlation
WeW0_at_cap = A * (W0_ref_rfp_max ** C)
We_ref_from_corr_at_cap = WeW0_at_cap * W0_ref_rfp_max

print("=== RFP Checks / References ===")
print(f"RFP max TOGW allowed [lb]         = {W0_ref_rfp_max:,.0f}")
print(f"Design governing TOGW [lb]        = {gov['W0']:,.0f}")
print("TOGW constraint check             =",
      "PASS" if gov["W0"] <= W0_ref_rfp_max else "FAIL")
print(f"Correlation-based empty @ 90k [lb]= {We_ref_from_corr_at_cap:,.0f} (for reference only)")

#
# 6) Major assumptions printout 


WS_target_lbft2 = 115.0  # major assumption (carrier approach driven; edit)
WS_implied = gov["W0"] / S_ref_ft2  # based on your OpenVSP model Sref

print("=== APPENDIX — Major Assumptions (brief) ===")
print(f"- One pilot only: pilot mass = {pilot_mass_kg:.1f} kg ({W_crew:.0f} lb total crew)")
print(f"- Payload definition includes RFP avionics = {W_avionics:.0f} lb + weapons + {stores_install_fraction*100:.0f}% install allowance")
print(f"- Fuel fraction inputs (given): R={R_nmi} nmi, E={E_hr} hr, TSFC={c_tsfc}, L/D={LD_cruise:.2f}, V={V_ms} m/s ({V_kt:.1f} kt)")
print(f"- Small segment fractions used: {segment_fracs}")
print(f"- Reserve factor: {reserve_factor:.2f}")
print(f"- Empty-weight fraction model (fighter): We/W0 = A * W0^C with A={A}, C={C}")
print(f"- OpenVSP parasite drag assumption: CD0_total = {CD0_total:.5f}")
print(f"- OpenVSP wetted area assumption: Swet = {S_wet_total_ft2:.2f} ft^2, Sref = {S_ref_ft2:.2f} ft^2")
print(f"  -> Wetted area ratio (Swet/Sref) = {wetted_ratio:.2f}")
print(f"- Wing loading target (assumed): W/S_target = {WS_target_lbft2:.1f} lb/ft^2")
print(f"- Wing loading implied by OpenVSP Sref at governing W0: W/S_implied = {WS_implied:.1f} lb/ft^2")
print(f"- RFP gross weight constraint reference: W0 <= {W0_ref_rfp_max:,.0f} lb")
