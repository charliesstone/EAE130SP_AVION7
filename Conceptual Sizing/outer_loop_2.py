import numpy as np
import inner_loop_2 as inner
import constraint_diagram as con
import matplotlib.pyplot as plt

S_grid = np.linspace(300, 600, 100)
T_grid = np.linspace(1, 60000, 100)
W0_guess = 47000 #this initial guess used is the TOGW of the F-18EF Super Hornet in lbf
T_guess = 40000 #this is some arbitrary reasonable guess for total thrust in lbf

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
    constraints = ["ceiling", "climb", "cruise_idl", "cruise_tar", "maneuver_idl", "maneuver_tar"]
    T_grid = {name: [] for name in constraints}
    W_grid = {name: [] for name in constraints}
    iterations_grid = []
    weight_iterations_grid = []

    for S_wing in S_grid:   #for loop to sweep across all S_grid values

        eps = 1e-6
        residual = []
        iterations = 0
        T_guess_dict = {
                "ceiling": T_guess,
                "climb": T_guess,
                "cruise_idl": T_guess,
                "cruise_tar": T_guess,
                "maneuver_idl": T_guess,
                "maneuver_tar": T_guess
            }
        
        while len(residual) == 0 or max(residual) > eps:

            residual = []
            #calculating a gross weight for each thrust from each constraint:
            #initializing TOGW dict
            TOGW = {}
            WS = {}
            #assigning the initial T_guess to all constraints
            
            for name in T_guess_dict:
                TOGW[name], weightiter = inner.loop(T_guess_dict[name], S_wing, W0_guess)
                weight_iterations_grid.append(weightiter)
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
            TW_reqmanuvidl, _, _ = con.maneuver_TW(WS=WS["maneuver_idl"], n=con.n_idl)
            TW_reqmanuvtar, _, _ = con.maneuver_TW(WS=WS["maneuver_tar"], n=con.n_tar)

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
                T_guess_dict[name] = 0.5*T_guess_dict[name] + 0.5*T_new_dict[name]
            iterations += 1
        
        for name in T_grid:
            T_grid[name].append(T_guess_dict[name])
        for name in W_grid:
            W_grid[name].append(TOGW[name])
        iterations_grid.append(iterations)

    return T_grid, W_grid

T_gridconverged, W_gridconverged = loop_TW(S_grid=S_grid, W0_guess=W0_guess, T_guess=T_guess)


#region plotting
# Convert lists to numpy arrays if needed
S = np.array(S_grid)

plt.figure(figsize=(10, 6))

# Plot each curve in T_gridconverged
for key, T_vals in T_gridconverged.items():
    T_array = np.array(T_vals)  # convert list to array
    plt.plot(S, T_array, label=key, linewidth=2)
# Add labels and title
plt.xlabel("Wing Area S (ft²)")
plt.ylabel("Thrust T (lbf)")
plt.title("Thrust Curves vs Wing Area")
plt.legend()
plt.grid(True)

# Show the plot
plt.tight_layout()
plt.show()


            

            
            

            



