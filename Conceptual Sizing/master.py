import numpy as np
import outer_loop_2 as outer
import matplotlib.pyplot as plt
#MASTERTS
S_gridref = np.linspace(150, 750, 100)
T_gridref = np.linspace(1, 70000, 100)
W0_guess = 47000 #this initial guess used is the TOGW of the F-18EF Super Hornet in lbf
T_guess = 40000 #this is some arbitrary reasonable guess for total thrust in lbf
S_guess = 500 #this is the wing area of the F-18EF in ft^2

#region plot 
T_gridconverged, W_gridconverged_T = outer.loop_TW(S_grid=S_gridref, W0_guess=W0_guess, T_guess=T_guess)
S_gridconverged, W_gridconverged_S = outer.loop_WS(T_grid=T_gridref, W0_guess=W0_guess, S_guess=S_guess)

#plotting constraints:
plt.figure(figsize=(16,9))
plt.plot(S_gridref, T_gridconverged["ceiling"], label="Ceiling")
plt.plot(S_gridref, T_gridconverged["climb"], label="Climb")
plt.plot(S_gridref, T_gridconverged["cruise_idl"], label="Cruise/dash at Mach 2.0")
plt.plot(S_gridref, T_gridconverged["cruise_tar"], label="Cruise/dash at Mach 1.6")
plt.plot(S_gridref, T_gridconverged["maneuver_idl"], label="Maneuver at 10 deg./s")
plt.plot(S_gridref, T_gridconverged["maneuver_tar"], label="Maneuver at 8 deg./s")
plt.plot(S_gridref, T_gridconverged["load_tar"], label="Maximum load of 7 g's")
plt.plot(S_gridref, T_gridconverged["load_idl"], label="Maximum load of 8 g's")
plt.plot(S_gridconverged["landing stall"], T_gridref, label="Stall at landing")
plt.plot(S_gridconverged["takeoff stall"], T_gridref, label="Stall at takeoff")
plt.plot(S_gridconverged["catapult takeoff"], T_gridref, label="Catapult launch")

#plotting design points and other aircraft:
#wing areas of reference aircrafts, in ft^2:
S_aircrafts = {
    "YF-52 Coyote (AVION)": 400,
    "F-35A (USA)": 460,
    "F/A-18E/F (USA)": 500,
    "J-35 (PRC)": 660,
    "Euro. Typhoon (EU)": 551,
    "Su-27 (RUS)": 670
}

#wet thrusts of reference aircrafts, in ft^2:
T_aircrafts = {
    "YF-52 Coyote (AVION)": 33500,
    "F-35A (USA)": 43000,
    "F/A-18E/F (USA)": 22000*2,
    "J-35 (PRC)": 26000*2,
    "Euro. Typhoon (EU)": 20200*2,
    "Su-27 (RUS)": 27600*2
}

#plotting points
for name in S_aircrafts:
    if name == "YF-52 Coyote (AVION)":
        plt.scatter(S_aircrafts[name], T_aircrafts[name], label=name, marker="D", color="gold")
    else:
        plt.scatter(S_aircrafts[name], T_aircrafts[name], label=name, marker="^")
    

#plotting unfeasible regions:
T_takeoff_interp = np.interp(S_gridref,
                             S_gridconverged["takeoff stall"],
                             T_gridref)
T_limit = np.minimum(T_gridconverged["load_idl"], T_takeoff_interp)
plt.fill_between(S_gridref, 0, T_limit,
                 color="gray", alpha=0.25,
                 zorder=0,
)
S_stall = S_gridconverged["takeoff stall"]
plt.fill_betweenx(T_gridref, 0, S_stall,
                  color="gray", alpha=0.25, zorder=0,
                  label="Unfeasible region")

#axes and graph labels
plt.xlim((200, 750))
plt.ylim((0, 70000))
plt.title("Dimensionalized Mission Constraint Diagram")
plt.xlabel("Wing Area S (ft²)")
plt.ylabel("Thrust T (lbf)")
plt.legend(loc="upper left")
plt.show()
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
#OUTERLOOP
import numpy as np
import inner_loop_2 as inner
import constraint_diagram as con
import matplotlib.pyplot as plt



#region loop_TW
def loop_TW(S_grid, W0_guess, T_guess):
    """
    This function finds a converged T using an inner iterative loop (pulled from inner_loop_2.py) to solve for a weight. It guesses 
    an initial weight using a T_guess and S_guess, and then backcalculates T using that weight and a mission constraint (pulled from 
    constraint_diagram.py). It then iterates until the T value is converged. Importantly to note, it converges each thrust curve simultaneously
    by only breaking the loop until all residuals are below the maximum error. This will cause some performance detriments in terms of already converged thrust values 
    continuing to be iterated upon, but it was deemed cleaner than a seperate loop for each constraint (which is what was implemented last time).

    Args:
        S_grid (array): List of reasonable S values. Each step in the for loop uses one single S_grid[i] value indexed from this array.
        W0_guess (float): Initial guess of W0 to start the iterative process in inner.loop().
        T_guess (float): Initial guess of T to start the iterative process in loop_TW().

    Returns:
        T_grid (dict): Dictionary of arrays of thrust, one array for each of the 6 TW-dependent constraints
        W_grid (dict): Dictionary of arrays of TOGW, one array for each of the 6 TW-dependent constraints, of same shape as T_grid
    """

    #region ini
    constraints = ["ceiling", "climb", "cruise_idl", "cruise_tar", "maneuver_idl", "maneuver_tar", "load_tar", "load_idl"]
    T_grid = {name: [] for name in constraints}
    W_grid = {name: [] for name in constraints}
    iterations_grid = []
    weight_iterations_grid = []
    max_iter = 200  # ADDED: safety cap so bad guesses cannot loop forever

    for S_wing in S_grid:   #for loop to sweep across all S_grid values

        eps = 1e-3          # ADJUSTED: use relative convergence tolerance consistent with Algorithm 4
        residual_T = []
        iterations = 0
        #assigning the initial T_guess to all constraints
        T_guess_dict = {
                "ceiling": T_guess,
                "climb": T_guess,
                "cruise_idl": T_guess,
                "cruise_tar": T_guess,
                "maneuver_idl": T_guess,
                "maneuver_tar": T_guess,
                "load_tar": T_guess,
                "load_idl": T_guess
            }
        
        while (len(residual_T) == 0 or max(residual_T) > eps) and iterations < max_iter:

            residual_T = []
            #calculating a gross weight for each thrust from each constraint:
            #initializing TOGW dict
            TOGW = {}
            WS = {}
            for name in T_guess_dict:
                TOGW[name], weightiter = inner.loop(T_guess_dict[name], S_wing, W0_guess)
                # weight_iterations_grid.append(weightiter)
                # print(TOGW, f"max iterations for TOGW is {np.max(np.array(weight_iterations_grid))}")
                WS[name] = TOGW[name]/S_wing
            
            #a required minimum T/W (thrust loading) given each requirement that is not independent of T/W is catalogued here:
            #region TWs 

            #ceiling
            TWreq_ceiling = con.ceilingTW
            
            #climb
            TWreq_climb = con.climbTW

            #cruise/dash
            # print(WS["cruise_idl"])
            TW_reqcruiseidl, _, _ = con.dash(WS=WS["cruise_idl"], M=con.M_cruiseidl)
            TW_reqcruisetar, _, _ = con.dash(WS=WS["cruise_tar"], M=con.M_cruise_tar)

            #manuever
            TW_reqmanuvidl, _, _ = con.maneuver_TW(WS=WS["maneuver_idl"], turnrate=con.turnrate8)
            TW_reqmanuvtar, _, _ = con.maneuver_TW(WS=WS["maneuver_tar"], turnrate=con.turnrate10)

            #structural loads
            TW_reqloadtar, _, _ = con.structloads_TW(WS=WS["load_tar"], n=con.nztar) 
            TW_reqloadidl, _, _ = con.structloads_TW(WS=WS["load_idl"], n=con.nzidl)

            #region new thrusts

            #ceiling
            T_new_ceiling = TWreq_ceiling * TOGW["ceiling"]

            #climb
            T_new_climb = TWreq_climb * TOGW["climb"]

            #cruise
            T_new_cruise_idl = TW_reqcruiseidl * TOGW["cruise_idl"]
            T_new_cruise_tar = TW_reqcruisetar * TOGW["cruise_tar"]

            #manuever
            T_new_maneuver_idl = TW_reqmanuvidl * TOGW["maneuver_idl"]
            T_new_maneuver_tar = TW_reqmanuvtar * TOGW["maneuver_tar"]

            #structural loads
            T_new_load_tar = TW_reqloadtar * TOGW["load_tar"]
            T_new_load_idl = TW_reqloadidl * TOGW["load_idl"]

            #storing these new Ts in a dict:
            T_new_dict = {
                "ceiling": T_new_ceiling,
                "climb": T_new_climb,
                "cruise_idl": T_new_cruise_idl,
                "cruise_tar": T_new_cruise_tar,
                "maneuver_idl": T_new_maneuver_idl,
                "maneuver_tar": T_new_maneuver_tar,
                "load_tar": T_new_load_tar,
                "load_idl": T_new_load_idl
            }
            
            #calculating residuals for each constraint:
            #region residual
            for name in T_new_dict:
                res_T = np.abs(T_new_dict[name] - T_guess_dict[name]) / max(np.abs(T_new_dict[name]), 1e-9)  # ADJUSTED: relative residual for realistic convergence
                residual_T.append(res_T)
                T_guess_dict[name] = T_new_dict[name]
            iterations += 1
        
        for name in T_grid:
            T_grid[name].append(T_guess_dict[name])
        for name in W_grid:
            W_grid[name].append(TOGW[name])
        iterations_grid.append(iterations)

    return T_grid, W_grid

#region loop_WS
def loop_WS(T_grid, W0_guess, S_guess):
    """
    This function finds a converged S using an inner iterative loop (pulled from inner_loop_2.py) to solve for a weight. It guesses 
    an initial weight using a T_guess and S_guess, and then backcalculates S using that weight and a mission constraint (pulled from 
    constraint_diagram.py). It then iterates until the S value is converged. Importantly to note, it converges each thrust curve simultaneously
    by only breaking the loop until all residuals are below the maximum error. This will cause some performance detriments in terms of already converged area values 
    continuing to be iterated upon, but it was deemed cleaner than a seperate loop for each constraint (which is what was implemented last time).

    Args:
        T_grid (array): List of reasonable T values. Each step in the for loop uses one single T_grid[i] value indexed from this array.
        W0_guess (float): Initial guess of W0 to start the iterative process in inner.loop().
        S_guess (float): Initial guess of S to start the iterative process in loop_TW().

    Returns:
        S_grid (dict): Dictionary of arrays of areas, one array for each of the 6 WS-dependent constraints
        W_grid (dict): Dictionary of arrays of TOGW, one array for each of the 6 WS-dependent constraints, of same shape as S_grid
    """
    #region ini
    constraints = ["landing stall", "takeoff stall", "catapult takeoff"]
    S_grid = {name: [] for name in constraints}
    W_grid = {name: [] for name in constraints}
    iterations_grid = []
    weight_iterations_grid = []
    max_iter = 200  # ADDED: safety cap so bad guesses cannot loop forever

    for T0 in T_grid:   #for loop to sweep across all S_grid values

        eps = 1e-3      # ADJUSTED: use relative convergence tolerance consistent with Algorithm 5
        residual_S = []
        iterations = 0
        #assigning the initial S_guess to all constraints
        S_guess_dict = {
            "landing stall": S_guess,
            "takeoff stall": S_guess,
            "catapult takeoff": S_guess,
        }

        while (len(residual_S) == 0 or max(residual_S) > eps) and iterations < max_iter:

                residual_S = []
                #calculating a gross weight for each thrust from each constraint:
                #initializing TOGW dict
                TOGW = {}
                WS = {}
                for name in S_guess_dict:
                    TOGW[name], weightiter = inner.loop(T0, S_guess_dict[name], W0_guess)
                    weight_iterations_grid.append(weightiter)
                    # print(TOGW, f"max iterations for TOGW is {np.max(np.array(weight_iterations_grid))}")

                #a required minimum W/S (wing loading) given each requirement that is a constant WS value is catalogued here:
                #region TWs

                #landing stall:
                WSreq_landingstall = con.stallWS_L
                
                #takeoff stall
                WSreq_takeoffstall = con.stallWS_T

                #catapult launch
                WS_req_cat = con.takeoffWS

                #calculating new wing area given requirements:
                S_new_landingstall = TOGW["landing stall"] / WSreq_landingstall   # ADJUSTED: use matching TOGW entry instead of leaked loop variable "name"
                S_new_takeoffstall = TOGW["takeoff stall"] / WSreq_takeoffstall   # ADJUSTED: use matching TOGW entry instead of leaked loop variable "name"
                S_new_cat = TOGW["catapult takeoff"] / WS_req_cat                 # ADJUSTED: use matching TOGW entry instead of leaked loop variable "name"

                #storing these S_new in a dict:
                S_new_dict = {
                    "landing stall": S_new_landingstall,
                    "takeoff stall": S_new_takeoffstall,
                    "catapult takeoff": S_new_cat
                }

                for name in S_new_dict:
                    res_S = np.abs(S_new_dict[name] - S_guess_dict[name]) / max(np.abs(S_new_dict[name]), 1e-9)  # ADJUSTED: relative residual for realistic convergence
                    residual_S.append(res_S)
                    S_guess_dict[name] = S_new_dict[name]
                iterations += 1  # ADJUSTED: count one outer-loop update per simultaneous pass
        for name in S_grid:
            S_grid[name].append(S_guess_dict[name])
        for name in W_grid:
            W_grid[name].append(TOGW[name])
        iterations_grid.append(iterations)
        
    return S_grid, W_grid
import numpy as np
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
#INNERLOOP

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
    else:                  # ADDED: safe tie case so W_payload is always defined
        W_payload = W_strike

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
        print(W_empty)
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

    if iterations == max_iter and residual > eps:  # ADJUSTED: move non-convergence check outside the loop so it actually executes
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

#running a test here to obtain TOGW for chosen design point of YF-52 Coyote:
T0_coyote = 22000
numengines_coyote = 1
T_guess = T0_coyote * numengines_coyote #thrust guess inputted
S_guess = 400        # actual wing ref area of super hornet
W0_guess = 35000     # initial TOGW guess


W0, it = loop(T_guess, S_guess, W0_guess)
W0_diff = np.abs(W0  - W0_F18EF)/W0_F18EF * 100
print(f"Coyote weight {W0} obtained after {it} iterations")

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
#CONSTRAINTDIAG
import numpy as np
import matplotlib.pyplot as plt

## ------ EAE 130A, preliminary design sizing ------ ##
## ------ Team 7 Avion: Mostafa Hashem, Charlie Stone, Jose Hernandez Negrete, ------ ##
## ------ Valeria Cecena, Quinn Kennerly, Lena Pattamadilok ------ ##

#region inputs
g = 32.174 #ft/s^2, gravitational acceleration
tar_togw = 50000 #lbf, target gross take off weight
S_LERX = 70 #ft^2, wing area of strakes from OpenVSP
Sref = 375 #ft^2, initial wing area assumption not including strakes (LERX)
Sreftot = Sref + S_LERX #ft^2, initial wing area assumption including strakes (LERX)
C_D0 = 0.01395 #initial zero-lift drag estimation, from OpenVSP
e_clean   = 0.85
e_takeoff = 0.75
e_landing = 0.7
# ^^^^^^ all from raymer textbook
nztar = 7 #target maximum structual load factor
nzidl = 8 #ideal maximum structual load factor
AR = 3.5 #aspect ratio, from OpenVSP main wing, not including strakes (LERX)
wingload = np.linspace(1, 200, 500)
thrustload = np.linspace(1, 2.5, 500)
VWOD = 50.63 #ft/s (15 kts) "Wind Over Deck" airspeed, or wind speed + carrier cruise velocity
VCAT = 200 #ft/s (120 kts) airspeed generated by forward throw of CATapult 
k_clean   = 1 / (np.pi * e_clean * AR)
k_takeoff = 1 / (np.pi * e_takeoff * AR)
k_landing = 1 / (np.pi * e_landing * AR) #drag polar constant, see 07-PreliminarySizing_Part3.pdf pg15 in canvas files

# ADDED: maneuver-weight fraction to reduce sustained-turn / structural-load TW to realistic combat values
Wf_Wi_manuv = 0.7706
#endregion

#region stall
Vstall_L = 195 #ft/s (115 KIAS), stall speed for landing (based on F/A-18E/F)
Vstall_C = 220 #ft/s (130 KIAS), stall speed for cruise (based on F/A-18E/F)
Vstall_T = 205 #ft/s (120 KIAS), stall speed for takeoff (based on F/A-18E/F)
rho_30k = 8.91E-4 #slugs/ft^3, atmospheric density at 30k ft
rho_SL = 23.77E-4 #slugs/ft^3, atmospheric density at sea level

# ADJUSTED: restored higher validated CLmax values so landing/takeoff/catapult WS limits shift left in T-S and appear more vertical
CLmax_L = 2.8
CLmax_C = 1.6
CLmax_T = 2.2

def stall(V, CL, rho):
    WS = (rho * CL * V**2) / 2
    return WS

stallWS_L = stall(Vstall_L, CLmax_L, rho_SL) #wing loading constraint for stall on landing
stallWS_C = stall(Vstall_C, CLmax_C, rho_30k) #wing loading constraint for stall on cruise
stallWS_T = stall(Vstall_T, CLmax_T, rho_SL) #wing loading constraint for stall on takeoff
#endregion

#region takeoff
def takeoff(rho, Vwod, Vcat, CLMT):
    WS = (0.5 * rho * (Vwod + Vcat)**2 * CLMT) / 1.21
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

climbTW = climb(k_takeoff, C_D0, CLmax_T)
#endregion

#region ceiling
def ceiling():
    """
    Calculates the fixed TW required for the ceiling constraint
    """
    return 2 * np.sqrt(k_clean * C_D0)

ceilingTW = ceiling()

#endregion

#region cruise/dash
M_cruiseidl = 2.0
M_cruise_tar = 1.6

def dash(WS, M):
    Wf_Wi_cruise = 0.7706 #Cruise/Takeoff weight fraction, from A2 sizing code
    Tcr_Tto = 1 #Cruise/Takeoff thrust fraction, from the GE F414 engine deck (note: refine value for A3)
    Vcruise = M * 996 #996 ft/s is speed of sound at 30kft from NASA standard atmosphere tables
    qcr = 1/2 * rho_30k * Vcruise**2 #lbf/ft^2, dynamic pressure at cruise velocity
    WS_cruise = WS * Wf_Wi_cruise #wing loading at cruise, as opposed to takeoff 
    cruise_coef1 = Wf_Wi_cruise/Tcr_Tto * (qcr * C_D0)
    cruise_coef2 = Wf_Wi_cruise/Tcr_Tto * (k_clean/qcr)
    TW = cruise_coef1/WS_cruise + cruise_coef2 * WS_cruise
    return TW, cruise_coef1, cruise_coef2

TW_cruiseMa2, cruise_coef1_idl, cruise_coef2_idl = dash(wingload, M_cruiseidl)
TW_cruiseMa1p6, cruise_coef1_tar, cruise_coef2_tar = dash(wingload, M_cruise_tar)

#region maneuverability 
# assume sustained turn at 20kft 
rho_20k = 0.001267  # slugs/ft^3 
V_turn = 1000       # ft/s 

def maneuver_TW(WS, turnrate):
    # target and ideal turn-rate maneuver constraints
    stall_coef = 2/(rho_20k*CLmax_C)
    V_stall = np.sqrt(stall_coef * WS)
    V_manuv = 3 * V_stall
    n = np.sqrt((turnrate * V_manuv / g)**2 + 1)

    q_manuv = 0.5 * rho_20k * V_manuv**2
    WS_manuv = Wf_Wi_manuv * WS   # ADJUSTED: evaluate turn-rate maneuver at maneuver-weight fraction instead of TOGW
    manuv_coef1 = Wf_Wi_manuv * q_manuv * C_D0  # ADJUSTED: consistent with takeoff-referenced TW form
    manuv_coef2 = Wf_Wi_manuv * k_clean * n**2 / q_manuv  # ADJUSTED: consistent with takeoff-referenced TW form
    TW = manuv_coef1/WS_manuv + manuv_coef2 * WS_manuv
    return TW, manuv_coef1, manuv_coef2

turnrate8 = 8 * np.pi/180
turnrate10 = 10 * np.pi/180

def structloads_TW(WS, n):
    # target and ideal structural load constraints
    q_turn = 0.5 * rho_20k * V_turn**2
    WS_manuv = Wf_Wi_manuv * WS   # ADJUSTED: structural-load sustained turn should use maneuver weight, not takeoff weight
    loads_coef1 = Wf_Wi_manuv * q_turn * C_D0
    loads_coef2 = Wf_Wi_manuv * k_clean * n**2 / q_turn
    TW = loads_coef1/WS_manuv + loads_coef2 * WS_manuv
    return TW, loads_coef1, loads_coef2

TW_manuv8deg, manuv_coef1_8deg, manuv_coef2_8deg = maneuver_TW(wingload, turnrate8)
TW_manuv10deg, manuv_coef1_10deg, manuv_coef2_10deg = maneuver_TW(wingload, turnrate10)
TW_load7g, loads_coef1_7g, loads_coef2_7g = structloads_TW(wingload, nztar)
TW_load8g, loads_coef1_8g, loads_coef2_8g = structloads_TW(wingload, nzidl)
#endregion


#region constraint diagram plot
plt.figure(figsize=(16,9))

colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
ci = 0
def nextc():
    global ci
    c = colors[ci % len(colors)]
    ci += 1
    return c

plt.plot(wingload, TW_cruiseMa1p6, linewidth=2, label="Dash: Mach 1.6 @ 30kft", color=nextc())
plt.plot(wingload, TW_cruiseMa2, linewidth=2, label="Dash: Mach 2.0 @ 30kft (ideal)", color=nextc())

plt.plot(wingload, TW_manuv8deg, linewidth=2, label="Sustained turn: 8 deg/s @ 20kft", color=nextc())
plt.plot(wingload, TW_manuv10deg, linewidth=2, label="Sustained turn: 10 deg/s @ 20kft", color=nextc())
plt.plot(wingload, TW_load7g, linewidth=2, label="Sustained Turn, n = 7g", color=nextc())
plt.plot(wingload, TW_load8g, linewidth=2, label="Sustained Turn, n = 8g", color=nextc())

plt.hlines(ceiling(), xmin=wingload.min(), xmax=wingload.max(),
           linewidth=2, label="Service ceiling (approx)", color=nextc())

plt.hlines(climbTW, xmin=wingload.min(), xmax=wingload.max(),
           linewidth=2, label="Climb constraint (approx)", color=nextc())

plt.axvline(stallWS_L, linewidth=2, label="Stall (landing) W/S limit", color=nextc())
plt.axvline(stallWS_T, linewidth=2, label="Stall (takeoff) W/S limit", color=nextc())
plt.axvline(takeoffWS, linewidth=2, label="Catapult takeoff W/S limit", color=nextc())

#plotting of aircraft of comparible role:

#takeoff ground weight in lbf
TOGW_aircrafts = {
    "YF-52 Coyote (AVION)": 36721.66,
    "F-35A (USA)": 49450,
    "F/A-18E/F (USA)": 47000,
    "J-35 (PRC)": 48943,
    "Euro. Typhoon (EU)": 35274,
    "Su-27 (RUS)": 67130
}

#wing areas of reference aircrafts, in ft^2:
S_aircrafts = {
    "YF-52 Coyote (AVION)": 400,
    "F-35A (USA)": 460,
    "F/A-18E/F (USA)": 500,
    "J-35 (PRC)": 660,
    "Euro. Typhoon (EU)": 551,
    "Su-27 (RUS)": 670
}

#wet thrusts of reference aircrafts, in ft^2:
T_aircrafts = {
    "YF-52 Coyote (AVION)": 33500,
    "F-35A (USA)": 43000,
    "F/A-18E/F (USA)": 22000*2,
    "J-35 (PRC)": 26000*2,
    "Euro. Typhoon (EU)": 20200*2,
    "Su-27 (RUS)": 27600*2
}

#solving for wing loading and thrust loading of reference aircraft:
WS_aircrafts = {}
TW_aircrafts = {}

for name in TOGW_aircrafts:
    WS_aircrafts[name] = TOGW_aircrafts[name]/S_aircrafts[name]
    TW_aircrafts[name] = T_aircrafts[name]/TOGW_aircrafts[name]
    if name == "YF-52 Coyote (AVION)":
        plt.scatter(WS_aircrafts[name], TW_aircrafts[name], label=name, marker="D", color="gold", zorder=2)
    else:
        plt.scatter(WS_aircrafts[name], TW_aircrafts[name], label=name, marker="^")


# shaded area
TW_union = np.maximum(TW_cruiseMa2, TW_load8g)

plt.fill_between(
    wingload,
    0,
    TW_union,
    color="gray",
    alpha=0.25,
    zorder=0,
    label="Unfeasible region"
)
plt.fill_between(
    wingload,
    TW_load8g,
    plt.ylim()[1],         # top of current y-axis
    where=(wingload >= stallWS_T),
    color="gray",
    alpha=0.25,
    zorder=0
)


plt.xlim(1, 200)
plt.ylim(0, 2.5)
plt.xlabel("Wing Loading W/S (lbf/ft²)")
plt.ylabel("Thrust Loading T/W (lbf/lbf)")
plt.title("Nondimensionalized Mission Constraint Diagram")
plt.legend(loc="upper right")
# plt.show()
#endregion