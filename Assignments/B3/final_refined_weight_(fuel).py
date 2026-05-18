import math
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple


# inputs

#  Geometry / drag polar 
S = 400.0               # ft^2, wing reference area
CD0 = 0.0144          # zero-lift drag coefficient #0.0144 for A2A, 0.0137 for Strike 
AR = 3.5                # aspect ratio
e = 0.75                # clean Oswald efficiency factor
k = 1.0 / (math.pi * e * AR)   # induced drag factor (0.123)

#  Atmosphere density (slug/ft^3) 
rho_sl = 0.002377
rho_10k = 0.001756
rho_20k = 0.001267
rho_30k = 0.000891

#  Speed of sound  (knots) 

a_sl_kts = 661.0
a_30k_kts = 589.33

#   Engine / fuel  
T_sl_max = 35000      # lbf, sea-level max dry thrust
T_idle = 0.05 * T_sl_max

# TSFC assumptions [1/hr]
ct_idle = 0.30          # taxi / idle (assumed slide-recommended value)
ct_dry = 0.34           # dry cruise / dry dash (found online for F117)
ct_max_dry = 0.9      # max dry thrust placeholder from fuel-flow / thrust ratio (assumed based on similar engines)
ct_climb = 0.8        # climb placeholder (assumed based on similar engines, climb typically higher than cruise))
ct_loiter = 0.30        # loiter placeholder (assumed slide-recommended value, typically similar to idle)

#   Recovery / descent assumptions  
# Historical placeholders, as mentioned in the lecture slides for descent / landing.
f_desc_30_to_0 = 0.990
f_desc_10k = f_desc_30_to_0 ** (1.0 / 3.0)     # 10k-ft descent placeholder
f_desc_20k = f_desc_30_to_0 ** (2.0 / 3.0)     # 20k-ft descent placeholder

#   Mission weights  
W0_strike = 37200     # lb, strike TOGW (iterated back and forth with B1(refined_weight).py,
# moved from 33,000 lb to 36,794 lb to 40,000 lb))

W0_a2a = 36200       # lb, A2A TOGW (iterated back and forth with B1(refined_weight).py
# moved from 30,000 lb to 34,000 lb to 38,700 lb)



#   Max fuel allowed     
fuel_fraction_max = 0.37
Wf_max_strike = fuel_fraction_max * W0_strike
Wf_max_a2a = fuel_fraction_max * W0_a2a

#   Recovery reserve requirement from RFP  
# RFP requires 20 min loiter at 10,000 ft + two landing attempts + 25% max fuel.

reserve_25pct_strike = 0.25 * Wf_max_strike
reserve_25pct_a2a = 0.25 * Wf_max_a2a

#   Go-around assumption  
go_around_minutes = 1.0   # timed go-around 
go_around_ct = ct_max_dry
go_around_thrust = T_sl_max

#   Combat / loiter   
# A2A combat speed placeholder 
V_combat_10k_kts = 460.0 # kts, historical placeholder combat speed at 10k ft
combat_minutes = 5.0

# A2A loiter time per your request
loiter_minutes = 30.0

#   Mission range budgeting assumptions  

R_total = 1000.0  # nm


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class SegmentResult:
    name: str
    start_weight_lb: float
    end_weight_lb: float
    fuel_burn_lb: float
    fuel_fraction: float
    notes: str = ""


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def thrust_scaled_with_density(rho: float) -> float:
    """
    Simple density-scaled dry thrust placeholder:
    T = T_sl_max * (rho / rho_sl)
    """
    return T_sl_max * (rho / rho_sl)


def taxi_takeoff_segment(W0: float) -> Tuple[SegmentResult, SegmentResult, float]:
    """
    Taxi and takeoff follow the lecture short-segment jet form:
      Wi+1 / Wi = 1 - t * ct * (T/W)
    """
    # Taxi: 15 min at idle
    t_taxi_hr = 15.0 / 60.0
    W1 = W0 * (1.0 - t_taxi_hr * ct_idle * (T_idle / W0))
    taxi = SegmentResult(
        name="Taxi / warm-up",
        start_weight_lb=W0,
        end_weight_lb=W1,
        fuel_burn_lb=W0 - W1,
        fuel_fraction=W1 / W0,
        notes="15 min at idle, idle thrust = 5% max thrust"
    )

    # Takeoff: 1 min at max dry thrust
    t_to_hr = 1.0 / 60.0
    W2 = W1 * (1.0 - t_to_hr * ct_dry * (T_sl_max / W1))
    takeoff = SegmentResult(
        name="Takeoff",
        start_weight_lb=W1,
        end_weight_lb=W2,
        fuel_burn_lb=W1 - W2,
        fuel_fraction=W2 / W1,
        notes="1 min at max dry thrust"
    )

    return taxi, takeoff, W2


def best_climb_state(W: float, rho: float, T: float) -> Tuple[float, float, float, float, float]:
    """
    Lecture best-rate climb speed for jets with quadratic drag polar.
    Returns:
      V_ft_s, D_lbf, Ps_ft_s, CL, CD
    """
    term = (T / W) + math.sqrt((T / W) ** 2 + 12.0 * CD0 * k)
    V = math.sqrt((W / S) / (3.0 * rho * CD0) * term)

    q = 0.5 * rho * V ** 2
    CL = W / (q * S)
    CD = CD0 + k * CL ** 2
    D = q * S * CD

    Ps = V * (T - D) / W
    return V, D, Ps, CL, CD


def climb_segment(
    W_start: float,
    delta_h_ft: float,
    rho: float,
    T: float,
    ct: float,
    name: str
) -> Tuple[SegmentResult, Dict[str, float]]:
    """
    Lecture climb fuel fraction for jets:
      Wi+1/Wi = exp( - ct * Delta_he / ( V * (1 - D/T) ) )
    Using constant-speed approximation: Delta_he ~= Delta_h
    """
    V, D, Ps, CL, CD = best_climb_state(W_start, rho, T)

    t_sec = delta_h_ft / Ps
    x_nm = V * t_sec / 6076.12

    exponent = - (ct / 3600.0) * delta_h_ft / (V * (1.0 - D / T))
    f = math.exp(exponent)
    W_end = W_start * f

    seg = SegmentResult(
        name=name,
        start_weight_lb=W_start,
        end_weight_lb=W_end,
        fuel_burn_lb=W_start - W_end,
        fuel_fraction=f,
        notes=f"Best-climb model, V={V:.1f} ft/s, x_climb={x_nm:.2f} nm"
    )

    extras = {
        "V_ft_s": V,
        "D_lbf": D,
        "Ps_ft_s": Ps,
        "CL": CL,
        "CD": CD,
        "x_climb_nm": x_nm,
        "time_sec": t_sec,
    }
    return seg, extras


def march_range_segment(
    W_start: float,
    R_seg_nm: float,
    N_steps: int,
    rho: float,
    V_kts: float,
    ct: float,
    name: str
) -> SegmentResult:
    """
     segmented exponential jet cruise / dash model:
      CL_i = 2 Wi / (rho V^2 S)
      CD_i = CD0 + k CL_i^2
      (L/D)_i = CL_i / CD_i
      Wi+1 = Wi * exp( -DeltaR * ct / (V * (L/D)_i) )
    """
    V_ft_s = V_kts * 1.68781
    dR = R_seg_nm / N_steps
    W = W_start

    for _ in range(N_steps):
        CL = 2.0 * W / (rho * V_ft_s ** 2 * S)
        CD = CD0 + k * CL ** 2
        LD = CL / CD
        W = W * math.exp(-dR * ct / (V_kts * LD))

    return SegmentResult(
        name=name,
        start_weight_lb=W_start,
        end_weight_lb=W,
        fuel_burn_lb=W_start - W,
        fuel_fraction=W / W_start,
        notes=f"Segmented range model, {N_steps} steps, V={V_kts:.1f} kt"
    )


def loiter_segment(
    W_start: float,
    endurance_hr: float,
    ct: float,
    name: str
) -> SegmentResult:
    """
    Lecture jet loiter model at max L/D:
      Wi+1 / Wi = exp( - E * ct / (L/D) )
    """
    LD_max = 1.0 / (2.0 * math.sqrt(CD0 * k))
    f = math.exp(-endurance_hr * ct / LD_max)
    W_end = W_start * f

    return SegmentResult(
        name=name,
        start_weight_lb=W_start,
        end_weight_lb=W_end,
        fuel_burn_lb=W_start - W_end,
        fuel_fraction=f,
        notes=f"Jet loiter at (L/D)_max={LD_max:.3f}"
    )


def descent_segment(W_start: float, fraction: float, name: str) -> SegmentResult:
    """
    Historical descent placeholder.
    """
    W_end = W_start * fraction
    return SegmentResult(
        name=name,
        start_weight_lb=W_start,
        end_weight_lb=W_end,
        fuel_burn_lb=W_start - W_end,
        fuel_fraction=fraction,
        notes="Historical descent fraction placeholder"
    )


def timed_thrust_segment(
    W_start: float,
    minutes: float,
    ct: float,
    thrust_lbf: float,
    name: str
) -> SegmentResult:
    """
    Short timed segment:
      Wi+1 / Wi = 1 - t * ct * (T/W)
    """
    t_hr = minutes / 60.0
    f = 1.0 - t_hr * ct * (thrust_lbf / W_start)
    if f <= 0.0:
        raise ValueError(f"Segment '{name}' produced nonphysical fuel fraction <= 0.")
    W_end = W_start * f
    return SegmentResult(
        name=name,
        start_weight_lb=W_start,
        end_weight_lb=W_end,
        fuel_burn_lb=W_start - W_end,
        fuel_fraction=f,
        notes=f"{minutes:.1f} min timed thrust segment"
    )


def print_mission_table(mission_name: str, results: List[SegmentResult]) -> None:
    print("\n" + "=" * 78)
    print(f"{mission_name}")
    print("=" * 78)
    print(f"{'Segment':35s} {'Start Wt':>12s} {'End Wt':>12s} {'Fuel Burn':>12s} {'Frac':>10s}")
    print("-" * 78)
    total_burn = 0.0
    for seg in results:
        total_burn += seg.fuel_burn_lb
        print(f"{seg.name:35s} "
              f"{seg.start_weight_lb:12.1f} "
              f"{seg.end_weight_lb:12.1f} "
              f"{seg.fuel_burn_lb:12.1f} "
              f"{seg.fuel_fraction:10.5f}")
    print("-" * 78)
    print(f"{'TOTAL MODELED FUEL BURN':35s} {'':12s} {'':12s} {total_burn:12.1f}")
    print("=" * 78)


# ============================================================
# STRIKE MISSION
# ============================================================

def run_strike_mission() -> List[SegmentResult]:
    results: List[SegmentResult] = []

    # 1) Taxi + takeoff
    taxi, takeoff, W = taxi_takeoff_segment(W0_strike)
    results += [taxi, takeoff]

    # 2) Climb to 30,000 ft
    T_30k = thrust_scaled_with_density(rho_30k)
    climb1, climb1_info = climb_segment(
        W_start=W,
        delta_h_ft=30000.0,
        rho=rho_30k,
        T=T_30k,
        ct=ct_climb,
        name="Climb 0 to 30,000 ft"
    )
    results.append(climb1)
    W = climb1.end_weight_lb
    x_climb = climb1_info["x_climb_nm"]

    # 3) strike range split
    # Placeholder interpretation based on the mission sketch:
    # total horizontal  = 1000 nm
    # includes initial climb distance + two 50 nm sea-level dashes + equal split of remaining range
    R_sea_level_dashes = 50.0 + 50.0
    R_remaining = R_total - x_climb - R_sea_level_dashes
    R_outbound_high = 0.5 * R_remaining
    R_return_high = 0.5 * R_remaining   # not flown below unless you decide to include it

    # 4) high-speed dash at 30k, Mach 2.0, max thrust 
    V_dash_30k_kts = 2.0 * a_30k_kts
    dash_out = march_range_segment(
        W_start=W,
        R_seg_nm=R_outbound_high,
        N_steps=20,
        rho=rho_30k,
        V_kts=V_dash_30k_kts,
        ct= 1.1, #afterburner-like thrust assumption for dash placeholder,
        name=f"Outbound dash Mach 2.0 at 30k ({R_outbound_high:.1f} nm)"
    )
    results.append(dash_out)
    W = dash_out.end_weight_lb

    # 5) Descent to sea level
    desc = descent_segment(W, f_desc_30_to_0, "Descent 30,000 ft to sea level")
    results.append(desc)
    W = desc.end_weight_lb

    # 6) Sea-level ingress dash, 50 nm, Mach 0.9, max dry thrust
    ingress = march_range_segment(
        W_start=W,
        R_seg_nm=50.0,
        N_steps=10,
        rho=rho_sl,
        V_kts=0.90 * a_sl_kts,
        ct=ct_dry,
        name="Ingress dash sea level, Mach 0.9, 50 nm"
    )
    results.append(ingress)
    W = ingress.end_weight_lb

    # 7) Sea-level egress dash, 50 nm, Mach 0.9
    egress = march_range_segment(
        W_start=W,
        R_seg_nm=50.0,
        N_steps=10,
        rho=rho_sl,
        V_kts=0.90 * a_sl_kts,
        ct=ct_dry,
        name="Egress dash sea level, Mach 0.9, 50 nm"
    )
    results.append(egress)
    W = egress.end_weight_lb

    # 8) Recovery reserve pieces required by RFP
    # 20 min loiter at 10k
    reserve_loiter = loiter_segment(
        W_start=W,
        endurance_hr=20.0 / 60.0,
        ct=ct_loiter,
        name="Recovery reserve loiter, 20 min at 10k"
    )
    results.append(reserve_loiter)
    W = reserve_loiter.end_weight_lb

    # 9) Two timed go-arounds
    ga1 = timed_thrust_segment(
        W_start=W,
        minutes=go_around_minutes,
        ct=go_around_ct,
        thrust_lbf=go_around_thrust,
        name="Go-around #1"
    )
    results.append(ga1)
    W = ga1.end_weight_lb

    ga2 = timed_thrust_segment(
        W_start=W,
        minutes=go_around_minutes,
        ct=go_around_ct,
        thrust_lbf=go_around_thrust,
        name="Go-around #2"
    )
    results.append(ga2)

    return results


# ============================================================
# AIR-TO-AIR MISSION
# ============================================================

def run_a2a_mission() -> List[SegmentResult]:
    results: List[SegmentResult] = []

    # 1) Taxi + takeoff
    taxi, takeoff, W = taxi_takeoff_segment(W0_a2a)
    results += [taxi, takeoff]

    # 2) Initial climb to 30,000 ft
    T_30k = thrust_scaled_with_density(rho_30k)
    climb1, climb1_info = climb_segment(
        W_start=W,
        delta_h_ft=30000.0,
        rho=rho_30k,
        T=T_30k,
        ct=ct_climb,
        name="Initial climb 0 to 30,000 ft"
    )
    results.append(climb1)
    W = climb1.end_weight_lb
    x_climb1 = climb1_info["x_climb_nm"]

    # 3)  loiter / combat / climb-back distances to determine range split
    # Loiter at 20k, 30 min, at max L/D
    CL_ldmax = math.sqrt(CD0 / k)
    # Use current weight as first-pass loiter-entry placeholder
    V_loiter_20k_ft_s = math.sqrt(2.0 * W / (rho_20k * S * CL_ldmax))
    V_loiter_20k_kts = V_loiter_20k_ft_s / 1.68781
    R_loiter = V_loiter_20k_kts * (loiter_minutes / 60.0)

    # Combat distance placeholder
    R_combat = V_combat_10k_kts * (combat_minutes / 60.0)

    # Climb-back  using updated representative weight will be computed after combat,
    # but we use a first-pass 20k-ft climb estimate to split the range budget.
    # Use a representative weight placeholder of 30,000 lb.
    T_20k = thrust_scaled_with_density(rho_20k)
    climb_back, climb_back_info = climb_segment(
        W_start=30000.0,
        delta_h_ft=20000.0,
        rho=rho_20k,
        T=T_20k,
        ct=ct_climb,
        name="Placeholder climb back 10k to 30k"
    )
    x_climb_back = climb_back_info["x_climb_nm"]

    # 4) Split remaining horizontal range evenly between outbound dash and return cruise
    R_remaining = R_total - x_climb1 - R_loiter - R_combat - x_climb_back
    R_dash_out = 0.5 * R_remaining
    R_return = 0.5 * R_remaining

    # 5) Dash at 30k, Mach 2.0 desired
    dash_out = march_range_segment(
        W_start=W,
        R_seg_nm=R_dash_out,
        N_steps=20,
        rho=rho_30k,
        V_kts=2.0 * a_30k_kts,
        ct=1.1, #afterburner-like thrust assumption for dash placeholder, lower than strike dash due to A2A loadout and climb-back requirement
        name=f"Dash Mach 2.0 at 30k ({R_dash_out:.1f} nm)"
    )
    results.append(dash_out)
    W = dash_out.end_weight_lb

    # 6) Descent 30k to 20k
    desc1 = descent_segment(W, f_desc_10k, "Descent 30,000 ft to 20,000 ft")
    results.append(desc1)
    W = desc1.end_weight_lb

    # 7) 30 min loiter at 20k
    loiter = loiter_segment(
        W_start=W,
        endurance_hr=loiter_minutes / 60.0,
        ct=ct_loiter,
        name="Loiter / acquire target, 30 min at 20k"
    )
    results.append(loiter)
    W = loiter.end_weight_lb

    # 8) Descent 20k to 10k
    desc2 = descent_segment(W, f_desc_10k, "Descent 20,000 ft to 10,000 ft")
    results.append(desc2)
    W = desc2.end_weight_lb

    # 9) Combat: 5 min at max dry thrust at 10k, placeholder
    T_10k = thrust_scaled_with_density(rho_10k)
    combat = timed_thrust_segment(
        W_start=W,
        minutes=combat_minutes,
        ct=1.2, #afterburner-like thrust assumption for combat placeholder, 
        thrust_lbf=T_10k,
        name="Combat, 5 min max dry at 10k"
    )
    results.append(combat)
    W = combat.end_weight_lb

    # 10) Climb back 10k to 30k with updated weight
    climb2, climb2_info = climb_segment(
        W_start=W,
        delta_h_ft=20000.0,
        rho=rho_20k,
        T=T_20k,
        ct=ct_climb,
        name="Climb back 10,000 ft to 30,000 ft"
    )
    results.append(climb2)
    W = climb2.end_weight_lb

    # 11) Return cruise, Mach 1.6 at 30k (required by RFP)
    return_cruise = march_range_segment(
        W_start=W,
        R_seg_nm=R_return,
        N_steps=20,
        rho=rho_30k,
        V_kts=1.6 * a_30k_kts,
        ct=ct_dry,
        name=f"Return cruise Mach 1.6 at 30k ({R_return:.1f} nm)"
    )
    results.append(return_cruise)
    W = return_cruise.end_weight_lb

    # 12) Descent to sea level
    desc3 = descent_segment(W, f_desc_30_to_0, "Descent 30,000 ft to sea level")
    results.append(desc3)
    W = desc3.end_weight_lb

    # 13) Recovery reserve loiter
    reserve_loiter = loiter_segment(
        W_start=W,
        endurance_hr=20.0 / 60.0,
        ct=ct_loiter,
        name="Recovery reserve loiter, 20 min at 10k"
    )
    results.append(reserve_loiter)
    W = reserve_loiter.end_weight_lb

    # 14) Two timed go-arounds
    ga1 = timed_thrust_segment(
        W_start=W,
        minutes=go_around_minutes,
        ct=go_around_ct,
        thrust_lbf=go_around_thrust,
        name="Go-around #1"
    )
    results.append(ga1)
    W = ga1.end_weight_lb

    ga2 = timed_thrust_segment(
        W_start=W,
        minutes=go_around_minutes,
        ct=go_around_ct,
        thrust_lbf=go_around_thrust,
        name="Go-around #2"
    )
    results.append(ga2)

    return results


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    strike_results = run_strike_mission()
    a2a_results = run_a2a_mission()

    print_mission_table("STRIKE MISSION", strike_results)
    print_mission_table("AIR-TO-AIR MISSION", a2a_results)

    print("\nAdditional reserve checks:")
    print(f"Strike 25% max fuel requirement: {reserve_25pct_strike:.1f} lb")
    print(f"A2A   25% max fuel requirement: {reserve_25pct_a2a:.1f} lb")

    print("\nNotes:")
    print("- This script includes the 20 min reserve loiter and two timed go-arounds.")
    print("- It does NOT add 50% store weight to arrestment landing weight; add that once store weights are finalized.")
    print("- Descent fractions are placeholders; replace with refined values if your team adopts different historical fractions.")
    print("- Mach 2.0 is treated here as a mission assumption for the dash segments.")
    print("- If your team later interprets the 1000 nm figure as true combat radius rather than the sketch’s total horizontal budget,")
    print("  update the range-splitting logic in run_strike_mission() and run_a2a_mission().")