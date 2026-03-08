psuedocode for reconstruction of T S diagram:

import drag polar here, updating the CD0 using the updated OpenVSP model

import T/W W/S diagram constraints here, noting which are constant in terms of W/S and which are constant in terms of T/W

inner loop weight function definition:

    guess a T_guess, S_guess, and W0_guess (TOGW). note that T_guess and S_guess are FIXED PARAMETERS inside this whole loop

    compute fuel fraction using mission constraints L_D_max, range in nm, endurance in hr, TSFC in lbm/(lbf hr) and cruise velocity in knots
    (adams calculate_weight_fraction() can be appropriated here)

    compute engine weight using T_guess

    compute empty weight using S_guess, the engine weight above (requiring T_guess), and W0_guess (for landing gear and all else calculations) along with fixed parameters S_ht, S_vt, S_wet_fuse, and num_engines

    calculate gross weight W0_new using engine weight, empty weight, and fixed parameters W_payload and W_crew

    calculate residual | W0_new - W0_guess |
    if residual not below mininum, W0_guess = W0_new and reloop
    output converged W0

outer loop thrust function definition for T/W CONSTRAINTS ONLY

    for loop to sweep across S_grid
        input a fixed S_grid[i] which is given by some S_wing np.linspace() at that station, additionally input a W0_guess to be fed into the inner lop function. this S_grid[i] is fed into the inner loop as S_guess. A certain initial guess for T, T0, is used and is also fed into the inner loop as T_guess

        feed parameters into inner loop and take iterated W0

        calculate a wing loading with W0/S_wing[i]

        feed this W0/S_wing[i] into the constraints on line 5, getting a T/Wreq from all the constraints that are T/W = f(W/S)

        calculate thrust such that T_new = T/Wreq * W0
        and check residual | T_new - T0 |
        if residual not below minimum, T0 = T_new and reloop
        output converged T0 and W0 given an S

    finish for loop
    output T_grid and W_grid of all converged T and W at each perscribed S

outer loop thrust function definition for W/S CONSTRAINTS ONLY
    for loop to sweep across T_grid
        input a fixed T_grid[i] which is given by some T0 np.linspace() at that station. additionally, input a W0_guess to be fed into the inner loop function. this T_grid[i] is fed into the inner loop as T_guess. A certain initial guess for S, S0, is used and fed into the inner loop as S_guess

        feed parameters into loop and take iterated W0 at perscribed T and our initial guess S_guess

        calculate a fixed required W/Sreq based on constraint parameters discussed in line 5

        calculate wing area such that S_new = (W/Sreq)^(-1) * W0
        check residual |S_new - S_guess |
        if residual not below minimum S_guess = S_new and reloop
        output converged S0 and W0 given a T

    finish for loop
    output S_grid and W_grid of all converged S and W at each perscribed T

plot each constraint based on whether or not they are WS or TW constraints