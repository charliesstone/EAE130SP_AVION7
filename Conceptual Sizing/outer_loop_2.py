import numpy as np
import inner_loop_2 as inner
import constraint_diagram as con

S_grid = np.linspace(1, 600, 100)
T_grid = np.linspace(1, 60000, 100)
W0_guess = 47000 #this initial guess used is the TOGW of the F-18EF Super Hornet in lbf

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
        T_guess (float): Initial guess of W0 to start the iterative process in loop_TW().

    Returns:
        T_grid_ceiling (array): Thrust values computed for the service ceiling constraint
            at each S_grid[i] station.

        W_grid_ceiling (array): Aircraft weight values corresponding to T_grid_ceiling
            for each S_grid[i] station.

        T_grid_climb (array): Thrust values computed for the climb constraint
            at each S_grid[i] station.

        W_grid_climb (array): Aircraft weight values corresponding to T_grid_climb
            for each S_grid[i] station.

        T_grid_cruise_idl (array): Thrust values computed for the ideal cruise/dash
            condition (Mach = M_cruiseidl) at each S_grid[i] station.

        W_grid_cruise_idl (array): Aircraft weight values corresponding to
            T_grid_cruise_idl for each S_grid[i] station.

        T_grid_cruise_tar (array): Thrust values computed for the target cruise/dash
            condition (Mach = M_cruise_tar) at each S_grid[i] station.

        W_grid_cruise_tar (array): Aircraft weight values corresponding to
            T_grid_cruise_tar for each S_grid[i] station.

        T_grid_maneuver_idl (array): Thrust values computed for the ideal sustained
            maneuver constraint (load factor = n_idl) at each S_grid[i] station.

        W_grid_maneuver_idl (array): Aircraft weight values corresponding to
            T_grid_maneuver_idl for each S_grid[i] station.

        T_grid_maneuver_tar (array): Thrust values computed for the target sustained
            maneuver constraint (load factor = n_tar) at each S_grid[i] station.

        W_grid_maneuver_tar (array): Aircraft weight values corresponding to
            T_grid_maneuver_tar for each S_grid[i] station.
    """

    #region ini
    constraints = ["ceiling", "climb", "cruise_idl", "cruise_tar", "maneuver_idl", "maneuver_tar"]
    T_grid = {name: [] for name in constraints}
    W_grid = {name: [] for name in constraints}
    iterations_grid = []

    for S_wing in S_grid:   #for loop to sweep across all S_grid values

        eps = 1e-6
        residual = []
        iterations = 0
        
        while len(residual) == 0 or max(residual) > eps:

            residual = []
            #calculating a gross weight for each thrust from each constraint:
            #initializing TOGW dict
            TOGW = {}
            WS = {}
            #assigning the initial T_guess to all constraints
            T_guess_ceiling, T_guess_climb, T_guess_cruise_idl, T_guess_cruise_tar, T_guess_maneuver_idl, T_guess_maneuver_tar = T_guess
            T_guess_dict = {
                "ceiling": T_guess_ceiling,
                "climb": T_guess_climb,
                "cruise_idl": T_guess_cruise_idl,
                "cruise_tar": T_guess_cruise_tar,
                "maneuver_idl": T_guess_maneuver_idl,
                "maneuver_tar": T_guess_maneuver_tar
            }
            for name in T_guess_dict:
                TOGW[name] = inner.loop(T_guess_dict[name], S_wing, W0_guess)
                WS[name] = TOGW[name]/S_wing

            #a required minimum T/W (thrust loading) given each requirement that is not independent of T/W is catalogued here:
            #region TWs 

            #ceiling
            TWreq_ceiling = con.ceilingTW
            
            #climb
            TWreq_climb = con.climbTW

            #cruise/dash
            TW_reqcruiseidl = con.dash(WS=WS["cruise_idl"], M=con.M_cruiseidl)
            TW_reqcruisetar = con.dash(WS=WS["cruise_tar"], M=con.M_cruise_tar)

            #manuever
            TW_reqmanuvidl = con.maneuver_TW(WS=WS["maneuver_idl"], n=con.n_idl)
            TW_reqmanuvtar = con.maneuver_TW(WS=WS["maneuver_tar"], n=con.n_tar)

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

            #storing these new Ts in a dict:
            T_new_dict = {
                "ceiling": T_new_ceiling,
                "climb": T_new_climb,
                "cruise_idl": T_new_cruise_idl,
                "cruise_tar": T_new_cruise_tar,
                "maneuver_idl": T_new_maneuver_idl,
                "maneuver_tar": T_new_maneuver_tar
            }
            
            #calculating residuals for each constraint:
            #region residual
            for name in T_new_dict:
                res = np.abs(T_new_dict[name] - T_guess_dict[name])
                residual.append(res)
                T_guess_dict[name] = T_new_dict[name]
            iterations += 1
        
        for name in T_grid:
            T_grid[name].append(T_guess_dict[name])
        for name in W_grid:
            W_grid[name].append(TOGW[name])
        iterations_grid.append(iterations)

print(T_grid)


            

            
            

            



