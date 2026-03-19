import numpy as np
import outer_loop_2 as outer
import matplotlib.pyplot as plt

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