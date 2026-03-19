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