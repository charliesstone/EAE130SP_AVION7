import numpy as np
import matplotlib.pyplot as plt
W_crew = 209 #lb
W_payload = 7335               #lb


V = 1065.2                     #knots, velocity
num_engines = 1                #jet engines, num of engines
T_0 = 45000                    #lbf, thrust
AR = 3.5                       #Aspect Ratio, unitless
c_f = 0.0026                   #Coeff. Friction
e = 0.825                        #Efficiency Factor
S_wet = 2044.71                #Wet area open vsp
S_ref = 573.00                 # ft^2
S_wing = 573.00             #Main wing area
C_D_0 = c_f * (S_wet / S_ref)
S_ht =   191.55648728                #Horizontal tail ft^2
S_vt = 92.259532089                  #Vertical Tail
S_wet_fuselage = 288.238328907
Wf_W0  = 0.3059
c = 0.75
L_D_max =10.81
E = 0.5 
R = 4000
#==========================================================
#ENGINE WEIGHT 
def calculate_engine_weight(T_0):
    W_eng_dry = 0.521 * T_0**0.9
    W_eng_oil = 0.082 * T_0**0.65
    W_eng_rev = 0.034 * T_0
    W_eng_control = 0.26 * T_0**0.5
    W_eng_start = 9.33 * (W_eng_dry/1000) ** 1.078
    W_eng = W_eng_dry + W_eng_oil + W_eng_rev + W_eng_control + W_eng_start
    return W_eng
#==========================================================
#EMPTY WEIGHT
def calculate_empty_weight(S_wing, S_ht, S_vt, S_wet_fuselage, TOGW, T_0 , num_engines):
    W_wing = S_wing * 10
    W_ht = S_ht * 5.5
    W_vt = S_vt * 5.5
    W_fuselage = S_wet_fuselage * 5
    W_landing_gear = 0.043 * TOGW
    Engine_weight = calculate_engine_weight(T_0)
    W_engines = Engine_weight * num_engines * 1.3
    W_all_else = 0.17 * TOGW
    W_empty = W_wing + W_ht + W_vt + W_fuselage + W_landing_gear + W_engines + W_all_else
    return W_empty
#===============================================================
#WEIGHT FRACTION

def calculate_weight_fraction(L_D_max, R, E, c, V):    
    L_D = 0.94 * L_D_max
    W3_W2 = np.exp((-R*c) / (V*L_D))  # cruise
    # print("Cruise Fuel Fraction (W3/W2): " + str(round(W3_W2, 3)))
    W4_W3 = np.exp((-E*c) / (L_D))    # loiter/descent
    # print("Loiter Fuel Fraction (W4/W3): " + str(round(W4_W3, 3)))
    W1_W0 = 0.99   # engine start & takeoff
    W2_W1 = 0.98   # climb
    W5_W4 = 0.995   # landing
    W5_W0 = W5_W4 * W4_W3 * W3_W2 * W2_W1 * W1_W0
    # print("Final Fuel Fraction (W5/W0): " + str(round(W5_W0, 3)))
    Wf_W0 = (1 - W5_W0) * 1.06    # compute fuel fraction
    # print("Total Fuel Fraction Wf/W0: {:.3f}".format(Wf_W0))
    return Wf_W0
#============================================================
#TAKE OFF GROSS WEIGHT LOOP

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
        Wf_W0 = calculate_weight_fraction(L_D_max, R, E, c, V)
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
#=========================================================

TOGW_guess = 500000  # Initial guess for Takeoff Gross Weight in pounds
final_TOGW, converged, iterations, W0_history = inner_loop_weight(
    TOGW_guess,
    S_wing, S_ht, S_vt, S_wet_fuselage,
    num_engines, W_crew, W_payload, T_0
)

# ploy the convergence history
plt.figure(figsize=(10,6))
plt.plot(W0_history, marker='o')
plt.title('Convergence of TOGW Estimate')
plt.xlabel('Iteration')
plt.ylabel('Estimated TOGW (lb)')
plt.grid()
plt.show()
print("Final estimated TOGW:", final_TOGW, "lb")

#FROM PREVIOUSLT DONE ASSIGNMENT A3
S_wing_grid = np.linspace(200, 800, 20)
coef_1_cruise_constraint = 0.02
coef_2_cruise_constraint = 0.00004

#================================================================
def outer_loop_thrust_for_one_constraint(
    S_wing_grid,
    TOGW_guess_init,
    T_total_guess_init,
    num_engines,
    S_ht, S_vt, S_wet_fuselage,
    W_crew, W_payload,
    coef_1_cruise_constraint, coef_2_cruise_constraint,
    tol_T_rel=1e-3,
    max_iter_T=100,
    relax=1.0
):

    T_total_converged = []
    W0_converged = []
    iter_counts = []
    T_total_history_allS = []

    for S_wing in S_wing_grid:

        T_total = T_total_guess_init
        T_hist = []

        for k in range(max_iter_T):

            T_0 = T_total / num_engines

            W0, wconv, it_w, W0_hist = inner_loop_weight(
                TOGW_guess_init,
                S_wing, S_ht, S_vt, S_wet_fuselage,
                num_engines, W_crew, W_payload, T_0
            )

            WS = W0 / S_wing

            TW_req = coef_1_cruise_constraint / WS + coef_2_cruise_constraint * WS
            T_req = TW_req * W0

            T_hist.append(T_total)

            if abs(T_req - T_total) / max(abs(T_total), 1e-9) < tol_T_rel:
                T_total = T_req
                break

            T_total = (1 - relax) * T_total + relax * T_req

        T_total_converged.append(T_total)
        W0_converged.append(W0)
        iter_counts.append(k + 1)
        T_total_history_allS.append(np.array(T_hist))

    return (
        np.array(T_total_converged),
        np.array(W0_converged),
        np.array(iter_counts),
        T_total_history_allS,
    )


# Plot the resulting T vs S curve from the outer loop convergence
T_actual_F18 = 17000
S_actual_F18 = 410
print(f'Actual T for F18: {T_actual_F18} lbf, Actual S for F18: {S_actual_F18} ft^2')

S_wing_grid = np.linspace(200, 800, 20)
#values at 30000 ft of altitude above the sea level.
rho = 8.9e-4      # slugs/ft^3 (ISA @ 40,000 ft)
a   = 995           # ft/s (ISA @ 40,000 ft)
M   = 2.0
V = M * a   
e_cruise = e
C_D_0 = 0.0190
C_D_0_cruise = C_D_0
def calculate_cruise_constraint_coefficients(rho, V, C_D_0, AR, e):
    q = 0.5 * rho * V**2   
    coef_1 = q * C_D_0
    coef_2 = 1/(np.pi * AR * e * q)
    return coef_1, coef_2
coef_1_cruise_constraint, coef_2_cruise_constraint = calculate_cruise_constraint_coefficients(rho, V, C_D_0_cruise, AR, e_cruise)
T_total_guess_init = 100000

T_total_curve, W0_curve, iters, T_histories = outer_loop_thrust_for_one_constraint(
    S_wing_grid,
    TOGW_guess,
    T_total_guess_init,
    num_engines,
    S_ht, S_vt, S_wet_fuselage,
    W_crew, W_payload,
    coef_1_cruise_constraint,
    coef_2_cruise_constraint
)

plt.figure(figsize=(16,9))
plt.title('Converged T vs S for Cruise Constraint')
plt.xlabel("Wing Area S (ft^2)")
plt.ylabel("Total Thrust T (lbf)")
plt.plot(S_actual_F18, T_actual_F18, label='Actual F18', marker='x', markersize=10, color='red')
plt.plot(S_wing_grid, T_total_curve, label='Converged T for Cruise Constraint', marker='o')
plt.legend(loc='best')
plt.grid()
plt.show()