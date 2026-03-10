import numpy as np
import outer_loop_2 as outer
import matplotlib.pyplot as plt

S_gridref = np.linspace(150, 750, 100)
T_gridref = np.linspace(1, 50000, 100)
W0_guess = 47000 #this initial guess used is the TOGW of the F-18EF Super Hornet in lbf
T_guess = 40000 #this is some arbitrary reasonable guess for total thrust in lbf
S_guess = 500 #this is the wing area of the F-18EF in ft^2

#region plot 
T_gridconverged, W_gridconverged_T = outer.loop_TW(S_grid=S_gridref, W0_guess=W0_guess, T_guess=T_guess)
S_gridconverged, W_gridconverged_S = outer.loop_WS(T_grid=T_gridref, W0_guess=W0_guess, S_guess=S_guess)

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
plt.xlim((200, 750))
plt.ylim((0, 50000))
plt.xlabel("Wing Area S (ft²)")
plt.ylabel("Thrust T (lbf)")
plt.legend()
plt.grid(True)
plt.show()