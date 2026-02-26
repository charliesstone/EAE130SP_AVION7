import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

## ------ EAE 130A, preliminary design sizing ------ ##
## ------ Team 7 Avion: Mostafa Hashem, Charlie Stone, Jose Hernandez Negrete, ------ ##
## ------ Valeria Cecena, Quinn Kennerly, Lena Pattamadilok ------ ##


#region drag polar
 
# Inputs you must set
 
AR = 4.5  # wing aspect ratio OpenVSP

C_D0 = 0.01755  # Clean CD0 OpenVSP 

#delta CD0 from slides
dCD0_takeoff_flaps = 0.015   # 0.010–0.020
dCD0_landing_flaps = 0.065   # 0.055–0.075
dCD0_gear          = 0.020   # 0.015–0.025

# Oswald e by stage from slides
e_clean   = 0.825  # 0.80–0.85
e_takeoff = 0.775  # 0.75–0.80
e_landing = 0.725  # 0.70–0.75

# CL max assumptions from raskom 
CLmax_clean   = 1.6
CLmax_takeoff = 2.0
CLmax_landing = 2.3

 
# region config table

configs = np.array([
    "Clean",
    "Takeoff flaps",
    "Takeoff flaps",
    "Landing flaps",
    "Landing flaps"
])

dCD0_flaps = np.array([
    0.0,
    dCD0_takeoff_flaps,
    dCD0_takeoff_flaps,
    dCD0_landing_flaps,
    dCD0_landing_flaps
])

dCD0_gear = np.array([
    0.0,
    0.0,
    dCD0_gear,
    0.0,
    dCD0_gear
])

e_values = np.array([
    e_clean,
    e_takeoff,
    e_takeoff,
    e_landing,
    e_landing
])

CL_max = np.array([
    CLmax_clean,
    CLmax_takeoff,
    CLmax_takeoff,
    CLmax_landing,
    CLmax_landing
])

# pandas dataframe
config_df = pd.DataFrame({
    "config": configs,
    "dCD0_flaps": dCD0_flaps,
    "dCD0_gear": dCD0_gear,
    "e": e_values,
    "CL_max": CL_max
})

#region computations
# Compute CD0 for each configuration using delta CD0
config_df["CD0_config"] = C_D0 + config_df["dCD0_flaps"] + config_df["dCD0_gear"]

# induced-drag factor k for each configuration (since e changes with flaps)
config_df["k"] = 1.0 / (math.pi * AR * config_df["e"])

print("\n=== Final CD0 per configuration (Clean + ΔCD0) ===")
print(config_df[["config", "CD0_config", "dCD0_flaps", "dCD0_gear", "e", "k"]].to_string(index=False))

 
#region plot 
 
plt.figure()

for _, row in config_df.iterrows():
    CL = np.linspace(-3.0, row["CL_max"], 900)  # CL from -4 to CLmax
    CD = row["CD0_config"] + row["k"] * (CL**2) 
    plt.plot(CD, CL, linewidth=1, label=row["config"])


plt.xlabel("C_D")
plt.ylabel("C_L")
plt.xlim(0, 0.30)
plt.xticks([0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30])
plt.ylim(-1.5, 1.5)
plt.title("Drag Polar")
plt.grid(True)
plt.legend()

#===============================================================================================================
#===============================================================================================================
#===============================================================================================================
#                                ._                             
#                               |* ;                            
#             `*-.              |"":                            
#              \  \             |""                             
#               .  \            |   :                           
#               `   \           |                               
#                \   \          |    ;               +.         
#                 .   \         |                   *._`-.      
#                 `    \        |     :          .-*'  `. `.    
#                 _\    \.__..--**--...L_   _.-*'      .'`*'    
#                /  `*-._\   -.       .-*"*+._       .'         
#               :        ``*-._*.     \      _J.   .'           
#           .-*'`*-.       ;     `.    \    /   `.'             
#       .-*'  _.-*'.     .-'       `-.  `-.:   _.'`-.           
#    +*' _.-*'      `..-'             `*-. `**'      `-.        
#     `*'          .-'      ._            `*-._         `.      
#               .-'         `.`-.____..+-**""'         .*"`.    
#          ._.-'          _.-*'''''-;._               /     `.  
#       .-'  `.      _.-*' `*-.__.-*   `"**--..__    :        `.
# .'..-'       \_.-*'                            `"**--..___.-*'
# `. `.    _.-*'                                                
#   `. `:*'                                                     
#     `. `.                                                     
#       `*
#===============================================================================================================
#===============================================================================================================
#===============================================================================================================

#region T/W W/S diagram
g = 32.174 #ft/s^2, gravitational acceleration
tar_togw = 50,000 #lbf, target gross take off weight
S_i = 600 #ft^2, initial wing area assumption including strakes (LERX)
S_ialt = 400 #ft^2, initial wing area assumption not including strakes (LERX)
e = 0.8 #oswald efficiency factor for fighters, from raymond textbook
AR = 3.5 #aspect ratio, from OpenVSP main wing, not including strakes (LERX)
nz_tar = 7.0 * g #ft/s^2, load factor, minimum targeted
nz_idl = 8.0 * g #ft/s^2, load factor, ideal targeted
wingload = np.linspace(0, 200, 500)
thrustload = np.linspace(0, 2.5, 500)
VWOD = 51 #ft/s (30 kts) "Wind Over Deck" airspeed, or wind speed + carrier cruise velocity
VCAT = 200 #ft/s (120 kts) airspeed generated by forward throw of CATapult 
k = 1/(np.pi * e * AR) #drag polar constant, see 07-PreliminarySizing_Part3.pdf pg15 in canvas files
#endregion

#region stall
Vstall_L = 195 #ft/s (115 KIAS), stall speed for cruise (based on F/A-18E/F)
Vstall_C = 220 #ft/s (130 KIAS), stall speed for landing (based on F/A-18E/F)
Vstall_T = 205 #ft/s (120 KIAS), stall speed for takeoff (based on F/A-18E/F)
rho_30k = 8.91E-4 #slugs/ft^3, atmospheric density at 30k ft
rho_SL = 23.77E-4 #slugs/ft^3, atmospheric density at sea level
CLmax_L = 2.0
CLmax_C = 1.5
CLmax_T = 1.7

def stall(V, CL, rho):
    WS = (rho * CL * V**2)/2
    return WS
stallWS_L = stall(Vstall_L, CLmax_L, rho_SL) #wing loading constraint for stall on landing
stallWS_C = stall(Vstall_C, CLmax_C, rho_30k) #wing loading constraint for stall on cruise
stallWS_T = stall(Vstall_T, CLmax_T, rho_SL) #wing loading constraint for stall on takeoff
#endregion

#region takeoff
def takeoff(rho, Vwod, Vcat, CLMT):
    WS = (0.5 * rho * (Vwod + Vcat)**2 * CLMT)/1.21
    return WS
takeoffWS = takeoff(rho_SL, VWOD, VCAT, CLmax_T) #wing loading constraint for clearing carrier runway on takeoff

#endregion

#region climb
#assume CLmax_climb = CLmax_T (takeoff)
def climb(k, Cd0, CLMCLB):
    ks = 3.4 #Vclimb ~ Vstall proportionality constant (using Vclimb 748 ft/s, MROC for Super Hornet, and Vstall_C)
    G = 0.220 #ft/ft (unitless) Climb Gradient, = sin(g) ~= g, where g = climb pitch angle
    tempoverinc = 1/(0.8) #loss of thrust due to 50F increase over standard temperature
    maxcont2max = 1/(0.94) #ratio of maximum continuous to maximum peak thrust
    TW_gen = (ks**2 * Cd0)/(CLMCLB) + k * (CLMCLB)/(ks**2) + G
    TW = tempoverinc * maxcont2max * TW_gen #other parameters not included, see 07-PreliminarySizing_Part3.pdf pg20
    return TW
climbTW = climb(k, C_D0, CLmax_T)
#endregion

#region ceiling
ceilingTW = 2 * np.sqrt(k * C_D0)
#endregion

#region climb/dash
M_cruiseidl = 2.0
M_cruise_tar = 1.6
def dash(Cd0, k, WS, M, rho):
    Wf_Wi_cruise = 0.7706 #Cruise/Takeoff weight fraction, from A2 sizing code
    Tcr_Tto = 22/13 #Cruise/Takeoff thrust fraction, from the GE F414 engine deck (note: refine value for A3)
    Vcruise = M * 996 #996 ft/s is speed of sound at 30kft from NASA standard atmosphere tables
    qcr = 1/2 * rho * Vcruise**2 #lbf/ft^2, dynamic pressure at cruise velocity
    WS_cruise = WS * Wf_Wi_cruise #wing loading at cruise, as opposed to takeoff
    TW = Wf_Wi_cruise/Tcr_Tto * ( (qcr * Cd0)/(WS_cruise) + k/qcr * (WS_cruise) ) #thrust loading at takeoff as a function of wing loading at cruise -> wing loading at takeoff
    return TW
TW_cruiseMa2 = dash(C_D0, k, wingload, M_cruiseidl, rho_30k)
TW_cruiseMa1p6 = dash(C_D0, k, wingload, M_cruise_tar, rho_30k)

#region maneuverability 
# assume sustained turn at 20kft 
rho_20k = 0.001267  # slugs/ft^3 
V_turn = 1000       # ft/s 
q_turn = 0.5 * rho_20k * V_turn**2

def maneuver_TW(WS, Cd0, k, q, n):
    # Sustained turn : T/W = D/W at load factor n
    return (q * Cd0) / WS + (k * n**2 * WS) / q

#target and ideal load factors
n_tar = 7.0   # target Nz
n_idl = 8.0   # ideal Nz

TW_manuv7g = maneuver_TW(wingload, C_D0, k, q_turn, n_tar)
TW_manuv8g = maneuver_TW(wingload, C_D0, k, q_turn, n_idl)
#endregion


#region plot
plt.figure(figsize=(10,6))

# --- Curves (T/W vs W/S) ---
plt.plot(wingload, TW_cruiseMa1p6, linewidth=2, label="Dash: Mach 1.6 @ 30kft")
plt.plot(wingload, TW_cruiseMa2,   linewidth=2, label="Dash: Mach 2.0 @ 30kft (ideal)")


# Maneuverability curves (choose whichever you implemented)
plt.plot(wingload, TW_manuv7g, linewidth=2, label="Sustained turn: 7g @ 20kft")  # if Option A
plt.plot(wingload, TW_manuv8g, linewidth=2, label="Sustained turn: 8g @ 20kft")  # if Option A
# plt.plot(wingload, TW_man_rate, linewidth=2, label="Sustained turn: 8 deg/s @ 20kft")  # if Option B

# Ceiling (horizontal line)
plt.hlines(ceilingTW, xmin=wingload.min(), xmax=wingload.max(),
           colors="k", linestyles="--", linewidth=2, label="Service ceiling (approx)")

# Climb (constant line in your current formulation)
plt.hlines(climbTW, xmin=wingload.min(), xmax=wingload.max(),
           colors="gray", linestyles="--", linewidth=2, label="Climb constraint (approx)")

# --- Vertical W/S limits ---
plt.axvline(stallWS_L, color="tab:red", linestyle="--", linewidth=2, label="Stall (landing) W/S limit")
plt.axvline(stallWS_T, color="tab:orange", linestyle="--", linewidth=2, label="Stall (takeoff) W/S limit")
plt.axvline(takeoffWS, color="tab:green", linestyle="--", linewidth=2, label="Catapult takeoff W/S limit")

# shaded area

TW_envelope = np.maximum.reduce([
    TW_cruiseMa1p6,
    TW_manuv7g,     # or TW_man_rate if using option B
    np.full_like(wingload, climbTW),
    np.full_like(wingload, ceilingTW),
])

# Max allowable W/S is the minimum of your W/S limits
WS_max = min(stallWS_L, stallWS_T, takeoffWS)

mask = wingload <= WS_max
plt.fill_between(wingload[mask], TW_envelope[mask], 2.5, alpha=0.15, label="Feasible region (T/W above constraints)")
#choosing design point

WS_design = 0.95 * WS_max  # near right edge of feasible region


TW_required_at_WS = np.interp(WS_design, wingload, TW_envelope)

# Adding small margin so it's inside the feasible region
margin = 1.08
TW_design = margin * TW_required_at_WS

print("\n=== Selected Design Point (bottom-right feasible) ===")
print(f"WS_design = {WS_design:.2f} lbf/ft^2")
print(f"TW_design = {TW_design:.3f}")
print ("landing stall speed", Vstall_L, "ft/s")
# Plot the design point on the constraint diagram
plt.scatter(WS_design, TW_design, s=120, marker="o", color="red", zorder=10, label="Design Point")

#plot design point comparison with F/A-18E/F Super Hornet
WS_FA18 = 85.0 #lbf/ft^2, wing loading of
TW_FA18 = 0.93 #thrust loading of F/A-18E/F Super Hornet, from A2 sizing code
plt.scatter(WS_FA18, TW_FA18, s=120, marker="X", color="blue", zorder=10, label="F/A-18E/F Super Hornet")   

#plot design point comparison with F-35C Lightning II
WS_F35 = 90.0 #lbf/ft^2, wing loading of F-35C Lightning II, from A2 sizing code    
TW_F35 = 0.87 #thrust loading of F-35C Lightning II, from A2 sizing code
plt.scatter(WS_F35, TW_F35, s=120, marker="D", color="green", zorder=10, label="F-35C Lightning II")    

#plot design point comparison with sukoi Su-57
WS_SU57 = 100.0 #lbf/ft^2, wing loading of Sukhoi Su-57, from A2 sizing code    
TW_SU57 = 1.09 #thrust loading of Sukhoi Su-57, from A2 sizing code
plt.scatter(WS_SU57, TW_SU57, s=120, marker="P", color="purple", zorder=10, label="Sukhoi Su-57")    
# plot

plt.xlim(0, 200)
plt.ylim(0, 2.5)
plt.xlabel("Wing Loading W/S (lbf/ft²)")
plt.ylabel("Thrust Loading T/W")
plt.title("Constraint Diagram: T/W vs W/S")
plt.grid(True)
plt.legend(loc="upper right")

print("\n=== Key W/S limits ===")
print("Landing stall W/S limit:", stallWS_L)
print("Takeoff stall W/S limit:", stallWS_T)
print("Catapult takeoff W/S limit:", takeoffWS)
print("Chosen WS_max:", WS_max)
#endregion

#===============================================================================================================
#===============================================================================================================
#===============================================================================================================
#                                ._                             
#                               |* ;                            
#             `*-.              |"":                            
#              \  \             |""                             
#               .  \            |   :                           
#               `   \           |                               
#                \   \          |    ;               +.         
#                 .   \         |                   *._`-.      
#                 `    \        |     :          .-*'  `. `.    
#                 _\    \.__..--**--...L_   _.-*'      .'`*'    
#                /  `*-._\   -.       .-*"*+._       .'         
#               :        ``*-._*.     \      _J.   .'           
#           .-*'`*-.       ;     `.    \    /   `.'             
#       .-*'  _.-*'.     .-'       `-.  `-.:   _.'`-.           
#    +*' _.-*'      `..-'             `*-. `**'      `-.        
#     `*'          .-'      ._            `*-._         `.      
#               .-'         `.`-.____..+-**""'         .*"`.    
#          ._.-'          _.-*'''''-;._               /     `.  
#       .-'  `.      _.-*' `*-.__.-*   `"**--..__    :        `.
# .'..-'       \_.-*'                            `"**--..___.-*'
# `. `.    _.-*'                                                
#   `. `:*'                                                     
#     `. `.                                                     
#       `*
#===============================================================================================================
#===============================================================================================================
#===============================================================================================================

#region T S Diagram

# Fixed parameters for weight estimation
L_D_max = 9
R = 1000            # nmi
E = 30 / 60         # min --> hr
c = 0.52            # lb/(lbf hr)
V = 291 * 1.94      # m/s --> knots
S_ht = 136.8093
S_vt = 70.3202
S_wet_fuselage = 288
num_engines = 1  # Example number of engines
num_pilot = 1
W_pilot = 200 #lbf
W_avionics = 2500.0  # [lb]
W_AIM9X  = 190   # [lb] 
W_MK83_JDAM = 1050  # [lb] 
W_payload = W_avionics + 4*W_MK83_JDAM + 2*W_AIM9X #Strike mission is used from 
# https://github.com/charliesstone/EAE130SP_AVION7/tree/main/Assignments/A2/Weight%26Cost/A2_weight_est_concept_2.py
#as it is more demanding than the air-to-air
# print(f"W_payload = {W_payload}")
# print(f"W_pilot = {W_pilot}")

#region weight defs
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
    W_wing = S_wing * 9
    W_ht = S_ht * 4
    W_vt = S_vt * 5.3
    W_fuselage = S_wet_fuselage * 4.8
    W_landing_gear = 0.045 * TOGW
    Engine_weight = calculate_engine_weight(T_0)
    W_engines = Engine_weight * num_engines * 1.3
    W_all_else = 0.17 * TOGW
    W_empty = W_wing + W_ht + W_vt + W_fuselage + W_landing_gear + W_engines + W_all_else
    return W_empty

def calculate_fuel_weight_fraction(L_D_max, R, E, c, V):
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

    W1_W0 = 0.990   # engine start & takeoff
    W2_W1 = 0.980   # climb
    W5_W4 = 0.995   # landing 
    #^^^^^ these have been changed from jupyter notebook values to values consistent with 
    # https://github.com/charliesstone/EAE130SP_AVION7/tree/main/Assignments/A2/Weight%26Cost/A2_weight_est_concept_2.py

    W5_W0 = W5_W4 * W4_W3 * W3_W2 * W2_W1 * W1_W0
    # print("Final Fuel Fraction (W5/W0): " + str(round(W5_W0, 3)))

    Wf_W0 = (1 - W5_W0) * 1.06    # compute fuel fraction
    # print("Total Fuel Fraction Wf/W0: {:.3f}".format(Wf_W0))

    return Wf_W0

#region inner loop def
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
        Wf_W0 = calculate_fuel_weight_fraction(L_D_max, R, E, c, V)
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

#region weight loop test

#these values are used as historical reference to give an estimate for the TOGW:
S_wing_ref_F18EF = 500 #ft^2
T0_ref_F18EF = 44000 #this is thrust value for both engines for the F-18E/F, since our num_engines is 1 for our design, to stay consistent

#initial TOGW guess
TOGW_guess = 50000 #lbf
final_TOGW, converged, iterations, W0_history = inner_loop_weight(TOGW_guess, S_wing_ref_F18EF, S_ht, S_vt,  S_wet_fuselage, num_engines, W_pilot, W_payload, T0_ref_F18EF)
# print(f"Converged Takeoff Gross Weight Estimate: {final_TOGW}")

#region thrust loop def
















# plt.show()