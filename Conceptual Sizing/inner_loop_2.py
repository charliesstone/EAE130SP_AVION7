import numpy as np

# # # # # # # # # # # # # # # # # # # # # # # 
# Fuel fraction function (A2 and A3)
# # # # # # # # # # # # # # # # # # # # # # # 
#region fuel frac
def calculate_weight_fraction(L_D_max, R, E, c, V):

    L_D = 0.94 * L_D_max

    W3_W2 = np.exp((-R*c) / (V*L_D))   # cruise
    W4_W3 = np.exp((-E*c) / (L_D))     # loiter

    W1_W0 = 0.990 # engine start and takeoff
    W2_W1 = 0.980 # climb
    W5_W4 = 0.995 #landing

    W5_W0 = W5_W4 * W4_W3 * W3_W2 * W2_W1 * W1_W0

    return (1 - W5_W0) * 1.06


# # # # # # # # # # # # # # # # # # # # # # # 
# Engine weight model (adams code)
# # # # # # # # # # # # # # # # # # # # # # # 
#region eng weight
def calculate_engine_weight(T0):

    W_eng_dry = 0.521 * T0**0.9
    W_eng_oil = 0.082 * T0**0.65
    W_eng_rev = 0.034 * T0
    W_eng_control = 0.26 * T0**0.5
    W_eng_start = 9.33 * (W_eng_dry/1000)**1.078

    return W_eng_dry + W_eng_oil + W_eng_rev + W_eng_control + W_eng_start


# # # # # # #
# Drag polar
# # # # # # #
#region drag polar
e_clean   = 0.85
e_takeoff = 0.75
e_landing = 0.7
def drag_polar(e):

    CD_0 = 0.01395    # from OpenVSP model circ. 3/6/26
    AR = 3.5        # From OpenVSP model circ. 3/6/26

    ## for mission segments, we could use different e values <----- i implemented this
    

    k = 1/(np.pi*AR*e)

    return CD_0, k


# # # # # # #
# INNER LOOP
# # # # # # #
#region inner loop
def loop(T_guess, S_guess, W0_guess):
    """
    This function finds a converged takeoff gross weight (TOGW) using iteration. It guesses 
    an initial weight using a T_guess and S_guess, and then backcalculates W using an engine thrust correlation calculate_engine_weight() and some simple area-based buildup techniques.
    It then iterates until the W value is converged given the fixed T_guess and S_guess. 

    Args:
        S_guess (float): Inputted wing area value.
        W0_guess (float): Initial guess of W0 to start the iterative process in inner.loop().
        T_guess (float): Inputted thrust value.

    Returns:
        W0_guess (float): Converged TOGW value.
        iterations (float): Number of iterations needed to reach a converged value. 
    """

    eps = 1e-6
    residual = 1
    iterations = 0

    # mission parameters
    L_D_max = 9            # CHANGE: max L/D estimate -- this is from raymer, later on we can use VSPAero
    R = 1000               # mission combat radius, from RFP
    E = 20/60              # loiter duration of 20 minutes outlined by the RFP
    c = 2.11               # TSFC in lbm/(lbf hr) for F135 engine using JP-10 or diesel fuel. From Sabzehali et. al. (pdf in root directory)
    V = 1989.09            # cruise speed for dash at altitude of 30k ft given M_a = 2.0 and U.S. Standard Atmosphere 1976 tables

    # aircraft constants
    num_engines = 1        # number of engines
    W_crew = 200           # pilot weight

    W_MK83_JDAM = 985      # weight of 1 MK83 bomb as per Jane's Weapons (Air Launched)
    W_AIM9X = 188          # weight of 1 AIM-9X sidewinder missile as per Jane's Weapons (Air Launched)
    W_AIM120C = 356        # weight of 1 AIM-120C missile as per Jane's Weapons (Air Launched)
    W_avionics = 2500       # general avionics payload weight
    W_strike = W_avionics + 4*W_MK83_JDAM + 2*W_AIM9X # weight for the loadout of the strike mission
    W_A2A = W_avionics + 6*W_AIM120C + 2*W_AIM9X # weight for the loadout of the air to air mission
    if W_strike > W_A2A:
        W_payload = W_strike
    elif W_A2A > W_strike: # <--------- using the heavier loadout weight for analysis
        W_payload = W_A2A

    S_ht = 140.25339        # horizontal tail area (from current openvsp model as of 3/6/26)
    S_vt = 140.64069        # vertical tail area (from current openvsp model as of 3/6/26)
    S_wet_fuselage = 385.39 # fuselage wetted area (from current openvsp model as of 3/6/26)
    max_iter = 100

    while residual > eps and iterations < max_iter:

        # # # # # # # #
        # Engine weight
        # # # # # # # #
        T0 = T_guess/num_engines
        Engine_weight = calculate_engine_weight(T0)

        # # # # # # # # # # #
        # Empty weight build-up
        # # # # # # # # # # #
        W_wing = S_guess * 9
        W_ht = S_ht * 4
        W_vt = S_vt * 5.3
        W_fuselage = S_wet_fuselage * 4.8

        W_landing_gear = 0.045 * W0_guess
        W_engines = Engine_weight * num_engines * 1.3
        W_all_else = 0.17 * W0_guess

        W_empty = W_wing + W_ht + W_vt + W_fuselage + W_landing_gear + W_engines + W_all_else

        # # # # # # # #
        # Drag polar
        # # # # # # # #
        # CD0, k = drag_polar(e_clean) # see below, not called

        # CL = math.sqrt(CD0/(3*k))
        # L_D = CL/(CD0 + k*CL**2) <-------- these are not called, what are they doing / why are they here? 
        # i commented them out idk 

        # # # # # # # #
        # Fuel weight
        # # # # # # # #
        Wf_W0 = calculate_weight_fraction(L_D_max, R, E, c, V)

        W_fuel = Wf_W0 * W0_guess

        # # # # # # # #
        # Update gross weight
        # # # # # # # #
        W0_new = W_empty + W_fuel + W_crew + W_payload

        residual = abs(W0_new - W0_guess)/W0_guess

        W0_guess = W0_new
        iterations += 1
        if iterations == max_iter:
            print(f"Warning: W0 did not converge for S={S_guess}, T={T_guess}")
            W0_guess = np.nan

    return W0_guess, iterations


# # # # # # # #
# Example run
# # # # # # # #
#region test of in. loop
# im running a test here to see if it gives me a reasonable value for the TOGW given
# the thrust and wing area of the super hornet
T0_F18EF = 22000
numengines_F18EF = 2
T_guess = T0_F18EF * numengines_F18EF #thrust guess inputted
S_guess = 500        # actual wing ref area of super hornet
W0_guess = 47000     # initial TOGW guess
W0_F18EF = 47000     # actual TOGW of super hornet

W0, it = loop(T_guess, S_guess, W0_guess)
W0_diff = np.abs(W0  - W0_F18EF)/W0_F18EF * 100
print(f"Compared to the Super Hornet's TOGW of {W0_F18EF}, the inner loop gives a value of {W0} after {it} iterations, which is {np.round(W0_diff, 1)}% inaccurate")