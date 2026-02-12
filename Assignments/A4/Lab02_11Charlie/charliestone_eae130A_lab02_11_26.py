import numpy as np 
import matplotlib.pyplot as plt

# -----------------------------------
# region ini val
# -----------------------------------

kg_to_lb = 2.2046226218
lb_to_kg = 1.0 / kg_to_lb

# Crew + Payload Inputs (ONE PILOT, NO PASSENGERS)

# Crew
n_pilots = 1
pilot_mass_kg = 95.0  # major assumption: pilot + gear (edit if you want)
W_crew = n_pilots * pilot_mass_kg * kg_to_lb  # [lb]

# Payload (edit these to match your RFP mission case)
# RFP says avionics/sensors weight = 2,500 lb internal
W_avionics = 2500.0  # [lb]

# Air-to-Air mission: 6x AIM-120C, 2x AIM-9X
W_AIM120 = 350  # [lb] 
W_AIM9X  = 190   # [lb] 
W_payload_AA = W_avionics + 6*W_AIM120 + 2*W_AIM9X

# -- Strike mission (RFP): 4x MK-83 JDAM, 2x AIM-9X
W_MK83_JDAM = 1050  # [lb] 
W_payload_STRIKE = W_avionics + 4*W_MK83_JDAM + 2*W_AIM9X

#performance inputs
R_nmi     = 2000
E_hr      = 0.5
c_tsfc    = 0.75
LD_cruise = 11.5 * 0.94
V_ms      = 548
V_kt      = V_ms * 1.9438444924  # nmi/hr

#geometry inputs
S_ht = 136.81
S_vt = 70.32
S_wet_fuselage = 288.26
num_engines = 1 #single-engined 

#iteration inputs
S_wing = 400 #ft^2, from OpenVSP model (this is for weight estimation, not wing area analysis)
S_wing_grid = np.linspace(275, 425, 100) #wing area mesh for analysis
T_0 = 22000 #lbf, from Super Hornet engine
TOGW_guess_init = 50000  # Initial guess for Takeoff Gross Weight in pounds
T_total_guess_init = 29500 #lbf, wet thrust from F110-GE-129 engine used in F-16C Block 50

#F-18E/F Super Hornet reference:
num_engines_F_18EF = 2
T_actual_F_18EF = 22000 * num_engines_F_18EF #lbf, actual thrust value from F-18E/F
S_actual_F_18EF = 500 #ft^2, actual wing area value from F-18E/F

#endregion

#region manuv

def maneuver_TW_coeffs(Cd0, k, q, n):
    # Sustained turn : T/W = D/W at load factor n
    coef_1_manuv_constraint = (q * Cd0)
    coef_2_manuv_constraint = (k * n**2) / q
    return coef_1_manuv_constraint, coef_2_manuv_constraint

C_D0 = 0.01755 #initial zero-lift drag estimation, from OpenVSP, see:
#(https://github.com/charliesstone/EAE130SP_AVION7/blob/main/Assignments/A2/Concepts/concept_1_COYOTE.vsp3)
e = 0.8 #oswald efficiency factor for fighters, from raymond textbook
AR = 4.5 #aspect ratio, from OpenVSP main wing, not including strakes (LERX)
k = 1/(np.pi * e * AR) #drag polar constant, see 07-PreliminarySizing_Part3.pdf pg15 in canvas files
rho_20k = 0.001267  # slugs/ft^3 
V_turn = 800       # ft/s 
q_turn = 0.5 * rho_20k * V_turn**2
n_tar = 7.0   # target Nz

coef_1_manuv_constraint, coef_2_manuv_constraint = maneuver_TW_coeffs(C_D0, k, q_turn, n_tar)


# -----------------------------------
# region w def inner loop
# -----------------------------------

def calculate_engine_weight(T_0):
    """Calculate the single engine weight based on the given thrust using empirical relationships.
    Args:
        T_0 (float): Thrust in pounds-force (lbf).
    Returns:
        float: Estimated engine weight in pounds (lb).
    """
    W_eng_dry = 0.521 * T_0**0.9
    W_eng_oil = 0.082 * T_0**0.65
    W_eng_rev = 0.034 * T_0
    W_eng_control = 0.26 * T_0**0.5
    W_eng_start = 9.33 * (W_eng_dry/1000) ** 1.078
    W_eng = W_eng_dry + W_eng_oil + W_eng_rev + W_eng_control + W_eng_start
    return W_eng

def calculate_empty_weight(S_wing, S_ht, S_vt, S_wet_fuselage, TOGW, T_0 , num_engines):
    """Calculate the empty weight based on empirical relationship buildup of components.
    Args:
        S_wing (float): Wing area (ft^2)
        S_ht (float): Horizontal stabilizer area (ft^2)
        S_vt (float): Vertical stabilizer area (ft^2)
        S_wet_fuselage (float): Wetted area of fuselage (ft^2)
        TOGW (float): Takeoff gross weight (lbf)
        T_0 (float): Dry sea level static thrust (lbf)
        num_engines (int): Number of engines

    Returns:
        float: Estimated empty weight in pounds (lbf).
    """
    SWMval = 9 #lbf/ft^2, wing multiplier via experimental data in roskam
    SHTMval = 4 #lbf/ft^2, htail multiplier via experimental data in roskam
    SVTMval = 5.3 #lbf/ft^2, vtail multiplier via experimental data in roskam
    FMval = 4.8 #lbf/ft^2, fuse multiplier via experimental data in roskam
    LGMval = 0.045 #lbf/ft^2, LG (Navy) multiplier via experimental data in roskam
    ALMval = 0.17 #lbf/ft^2, all else multiplier via experimental data in roskam
    W_wing = S_wing * SWMval
    W_ht = S_ht * SHTMval
    W_vt = S_vt * SVTMval
    W_fuselage = S_wet_fuselage * FMval
    W_landing_gear = LGMval * TOGW
    Engine_weight = calculate_engine_weight(T_0)
    W_engines = Engine_weight * num_engines * 1.3
    W_all_else = ALMval * TOGW
    W_empty = W_wing + W_ht + W_vt + W_fuselage + W_landing_gear + W_engines + W_all_else
    return W_empty

def calculate_weight_fraction(L_D_max, R, E, c, V):
    """This function calculates the weight fractions for cruise and loiter/descent phases based on the Breguet range and endurance equations, and also other terms.
    Args:
        L_D_max (float): Maximum lift-to-drag ratio of the aircraft.
        R (float): Range in nautical miles.
        E (float): Endurance in hours.
        c (float): Specific fuel consumption in lb/(lbf hr).
        V (float): Velocity in knots."""
    
    L_D = 0.94 * L_D_max

    W3_W2 = np.exp((-R*c) / (V*L_D))  # cruise
    # print("Cruise Fuel Fraction (W3/W2): " + str(round(W3_W2, 3)))

    W4_W3 = np.exp((-E*c) / (L_D))    # loiter/descent
    # print("Loiter Fuel Fraction (W4/W3): " + str(round(W4_W3, 3)))

    W1_W0 = 0.970   # engine start & takeoff
    W2_W1 = 0.985   # climb
    W5_W4 = 0.995   # landing

    W5_W0 = W5_W4 * W4_W3 * W3_W2 * W2_W1 * W1_W0
    # print("Final Fuel Fraction (W5/W0): " + str(round(W5_W0, 3)))

    Wf_W0 = (1 - W5_W0) * 1.06    # compute fuel fraction
    # print("Total Fuel Fraction Wf/W0: {:.3f}".format(Wf_W0))

    return Wf_W0

#endregion

# -----------------------------------
# region inner loop ini
# -----------------------------------

def inner_loop_weight(
    TOGW_guess,
    S_wing, S_ht, S_vt, S_wet_fuselage,
    num_engines, w_crew, w_payload, T_0,
    err=1e-6,
    max_iter=200
):
    W0_history = []
    delta = np.inf
    it = 0

    while delta > err and it < max_iter:
        # 1) fuel fraction (could be constant or updated)
        Wf_W0 = calculate_weight_fraction(L_D_max=LD_cruise, R=R_nmi, E=E_hr, c=c_tsfc, V=V_kt)
        W_fuel = Wf_W0 * TOGW_guess

        # 2) empty weight based on current TOGW guess + geometry + thrust
        W_empty = calculate_empty_weight(
            S_wing, S_ht, S_vt, S_wet_fuselage,
            TOGW_guess, T_0, num_engines
        )

        # 3) new gross weight
        W0_new = W_empty + w_crew + w_payload + W_fuel
        W0_history.append(W0_new)

        # 4) convergence check
        delta = abs(W0_new - TOGW_guess) / max(abs(W0_new), 1e-9)

        # 5) update
        TOGW_guess = W0_new
        it += 1

    converged = (delta <= err)
    return TOGW_guess, converged, it, np.array(W0_history)

#endregion

#region inner loop exe
if W_payload_AA > W_payload_STRIKE:
    W_payload = W_payload_AA
if W_payload_AA <= W_payload_STRIKE:
    W_payload = W_payload_STRIKE
final_TOGW, converged, iterations, W0_history = inner_loop_weight(
    TOGW_guess_init,
    S_wing, S_ht, S_vt, S_wet_fuselage,
    num_engines, W_crew, W_payload, T_0
)

# plt.figure(figsize=(10,6))
# plt.plot(W0_history, marker='o')
# plt.title('Convergence of TOGW Estimate')
# plt.xlabel('Iteration')
# plt.ylabel('Estimated TOGW (lb)')
# plt.grid()
# plt.show()
# print("Final estimated TOGW:", final_TOGW, "lb")

#region outer loop ini

def outer_loop_thrust_for_one_constraint(
    S_wing_grid,
    TOGW_guess_init,
    T_total_guess_init,      # total thrust guess (all engines), lbf
    num_engines,
    S_ht, S_vt, S_wet_fuselage,
    W_crew, W_payload,
    coef_1_manuv_constraint, coef_2_manuv_constraint,
    tol_T_rel=1e-3,          
    max_iter_T=100,
    relax=0.15              # optional damping: 0.3~1.0 (use <1 if oscillation)
):
    
    T_total_converged = []
    W0_converged = []
    iter_counts = []
    T_total_history_allS = []  # list of arrays (one per S)

    for S_wing in S_wing_grid:

        # Initialize outer loop for this S
        T_total = T_total_guess_init
        TOGW_guess = TOGW_guess_init

        T_hist = []

        for k in range(max_iter_T):
            # Convert total thrust to per-engine thrust for the weight model
            T_0 = T_total / num_engines

            # Inner loop: converge weight for (S, T_0)
            W0, wconv, it_w, W0_hist = inner_loop_weight(
                TOGW_guess,
                S_wing, S_ht, S_vt, S_wet_fuselage,
                num_engines, W_crew, W_payload, T_0
            )

            # Wing loading from converged weight
            WS = W0 / S_wing

            # Constraint equations: compute required T/W from W/S
            # For lab: just maneuver:
            TW_req = coef_1_manuv_constraint/WS + coef_2_manuv_constraint*WS
            
            # Required total thrust
            T_req = TW_req * W0

            # Store history
            T_hist.append(T_total)

            # Check outer convergence
            if abs(T_req - T_total) / max(abs(T_total), 1e-9) < tol_T_rel:
                T_total = T_req
                break

            # Update thrust (optionally relaxed damping)
            T_total = (1 - relax) * T_total + relax * T_req

        # Save results for this S
        T_total_converged.append(T_total)
        W0_converged.append(W0)
        iter_counts.append(k+1)
        T_total_history_allS.append(np.array(T_hist))

    return (np.array(T_total_converged),
            np.array(W0_converged),
            np.array(iter_counts),
            T_total_history_allS,
            W0, wconv, it_w, W0_hist)

#endregion


#region outer loop exe
T_total_curve, W0_curve, n_iter_T, T_hist_allS, W0_final, wconv_final, it_w_final, W0_hist_final = outer_loop_thrust_for_one_constraint(
    S_wing_grid=S_wing_grid,
    TOGW_guess_init=TOGW_guess_init,
    T_total_guess_init=T_total_guess_init,
    num_engines=num_engines,
    S_ht=S_ht, S_vt=S_vt, S_wet_fuselage=S_wet_fuselage,
    W_crew=W_crew, W_payload=W_payload,
    coef_1_manuv_constraint=coef_1_manuv_constraint,
    coef_2_manuv_constraint=coef_2_manuv_constraint,
    tol_T_rel=1e-6,
    max_iter_T=200,
    relax=0.15
)

# # print(f'Actual T for F-18E/F Super Hornet: {T_actual_F_18EF} lbf, Actual S for F-18E/F: {S_actual_F_18EF} ft^2')

# plt.figure(figsize=(16,9))
# plt.title('Converged T vs S for Cruise Constraint')
# plt.xlabel("Wing Area S (ft^2)")
# plt.ylabel("Total Thrust T (lbf)")
# # plt.plot(S_actual_F_18EF, T_actual_F_18EF, label='Actual 777', marker='x', markersize=10, color='red')
# plt.plot(S_wing_grid, T_total_curve, label='Converged T for Cruise Constraint', marker='o')
# plt.legend(loc='best')
# plt.grid()
# plt.show()