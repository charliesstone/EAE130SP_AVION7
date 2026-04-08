#Modified Constraints
import numpy as np

# Inputs
W0 = 36700
#Altitude changes
h_start = 0
h_end = 30000
N = 500

ct = 1.9 / 3600   # convert to 1/s
V = 748           # ft/s
Cd0 = 0.01755
k = 0.05          # corrected
S = 400           # ft^2
T = 33500         # lbf

# Density function
def rho_std(h):
    rho0 = 0.0023769
    T0 = 518.67
    L = 0.00356616
    g = 32.174
    R = 1716

    return rho0 * (1 - (L * h) / T0)**((g / (R * L)) - 1)

# CLIMB REGION
import numpy as np

def climb_fuel_x(W0, h_start, h_end, N, ct, V, Cd0, k, S, rho_std, T):

    W = W0  #Initial guess
    dh = (h_end - h_start) / N #discretizing altitude

    x_climb = 0  # total horizontal distance

    for i in range(N):
        h = h_start + i * dh
        rho = rho_std(h)

        # Lift = Weight
        CL = W / (0.5 * rho * V**2 * S)

        # Drag
        CD = Cd0 + k * CL**2
        D = 0.5 * rho * V**2 * S * CD

        # --- FUEL UPDATE ---
        dhe = dh
        W = W * np.exp(-ct * dhe / (V * (1 - D / T)))

        # --- DISTANCE UPDATE ---
        dx = dh * W / (T - D)

        x_climb += dx

    return W, x_climb

# Run
W_final_climb,x_climb = climb_fuel_x(W0, h_start, h_end, N, ct, V, Cd0, k, S, rho_std, T)

fuel_climb = W0 - W_final_climb

Fuel_Fraction_Climb = W_final_climb/W0

print("Final Weight [lb]:", W_final_climb)
print("Fuel Burned in Climb [lb]:", fuel_climb)
print("Horizontal Climb Distance [nm]:", x_climb/6076)
print("Climb Fuel Weight Fraction W_final/W0:",Fuel_Fraction_Climb)

#CRUISE REGION 

def cruise_fuel(W0, R_total, N, ct, V, Cd0, k, S, rho):

    W = W0
    dR = R_total / N

    for i in range(N):

        # Lift = Weight → get CL
        CL = W / (0.5 * rho * V**2 * S)

        # Drag coefficient
        CD = Cd0 + k * CL**2

        # Drag = Thrust required
        D = 0.5 * rho * V**2 * S * CD

        T = D  # steady cruise

        # Fuel burned in this segment
        dW = ct * T * (dR / V)

        # Update weight
        W = W - dW

    return W


#Velocity from Mach
def velocity(M):
    R = 1716
    T = 389.67 #Rankine, temperature at 30kft. 
    gamma = 1.4
    R = 1716
    a = np.sqrt(gamma*R*T)
    V = M*a
    return V

R_tot = 700 * 6076 #nm to ft

V_M2 = velocity(2)
V_M1p6 = velocity(1.6)
rho_30k = 8.91E-4 #slugs/ft^3, atmospheric density at 30k ft

#Cruise mach 2.0 
W_final_2 = cruise_fuel(W_final_climb, R_tot, N, ct, V_M2, Cd0, k, S, rho_30k)

#Cruise at mach 1.6

W_final_1p6 = cruise_fuel(W_final_climb, R_tot, N, ct, V_M1p6, Cd0, k, S, rho_30k)

print("Final Weight Cruise M = 2.0:", W_final_2)
print("Final Weight cruise M=1.6:", W_final_1p6)
