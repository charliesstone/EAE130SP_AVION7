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
    constraint_diagram.py). It then iterates until the T value is converged. 

    Args:
        S_grid (array): List of reasonable S values. Each step in the for loop uses one single S_grid[i] value indexed from this array.
        W0_guess (float): Initial guess of W0 to start the iterative process in inner.loop().
        T_guess (float): Initial guess of W0 to start the iterative process in loop_TW().

    Returns:
        T_grid (array): An array of each iteratively solved T value at each S_grid[i] station.
        W_grid (array): An array of each iteratively solved W value, given the corresponding T value with the same index in T_grid, for each S_grid[i] station
    """

    for S_wing in S_grid:   #for loop to sweep across all S_grid values

        TOGW = inner.loop(T_guess, S_wing, W0_guess) #finding an initial weight based off initial T_guess
        WS = TOGW/S_wing

        #a required minimum T/W (thrust loading) given each requirement that is not independent of T/W is catalogued here:
        #region loop_TW const
        TWreq_ceiling = con.ceilingTW
        TWreq_climb = con.climbTW
        TW_reqcruiseidl = con.dash()

