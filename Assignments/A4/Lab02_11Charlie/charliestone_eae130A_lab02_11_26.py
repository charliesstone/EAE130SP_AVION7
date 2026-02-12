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





# -----------------------------------
# region iter loop ini
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





def iterate_TOGW(W_payload, W_crew, fuel_frac, W0_guess=80000.0, err=1e-6, max_iter=200):
    """Calculate the TOGW based off fuel fraction and payload weight
    Args:
        W_payload (float): Weight of total payload in pounds-force (lbf).
        W_crew (float): Weight of crew in pounds-force (lbf).
        fuel_frac (float): Fuel fraction on takeoff.
        W0_guess (float): Initial guess of TOGW in pounds-force (lbf).
        err (float): iteration maximum allowed error
        max_iter: maximum allowed iterations
    Returns:
        float: estimated TOGW (lb).
    """
    W0 = float(W0_guess)
    for i in range(max_iter):
        We_W0 = A * (W0 ** C)
        denom = 1.0 - fuel_frac - We_W0
        W0_new = (W_payload + W_crew) / denom
        delta = abs(W0_new - W0) / abs(W0_new)
        W0 = W0_new
        if delta < err:
            return W0, We_W0, i+1, delta
    return W0, A * (W0 ** C), max_iter, delta