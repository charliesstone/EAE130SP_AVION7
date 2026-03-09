import numpy as np
import outer_loop_2 as outer
import matplotlib.pyplot as plt

S_gridref = np.linspace(150, 750, 100)
T_gridref = np.linspace(1, 60000, 100)
W0_guess = 47000 #this initial guess used is the TOGW of the F-18EF Super Hornet in lbf
T_guess = 40000 #this is some arbitrary reasonable guess for total thrust in lbf
S_guess = 500 #this is the wing area of the F-18EF in ft^2

#region plot 
T_gridconverged, W_gridconverged_T = outer.loop_TW(S_grid=S_gridref, W0_guess=W0_guess, T_guess=T_guess)
S_gridconverged, W_gridconverged_S = outer.loop_WS(T_grid=T_gridref, W0_guess=W0_guess, S_guess=S_guess)

plt.figure(figsize=(16,9))
for name in T_gridconverged:
    plt.plot(S_gridref, T_gridconverged[name], label=f"{name} TW")
for name in S_gridconverged:
    plt.plot(S_gridconverged[name], T_gridref, label=f"{name} WS")
plt.xlim((200, 750))
plt.ylim((0, 60000))
plt.xlabel("Wing Area S (ft²)")
plt.ylabel("Thrust T (lbf)")
plt.legend()
plt.grid(True)
plt.show()