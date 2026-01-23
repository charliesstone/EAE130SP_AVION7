# Weight Demo 

import math
import numpy as np
import matplotlib.pyplot as plt


# num of ppl 
n_pilots = 2
n_attendants = 12
n_passengers = 314
m_passenger_kg = 82
m_luggage_kg = 27
m_crew_kg = 82
kg_to_lb = 2.2046226218

W_payload = n_passengers * (m_passenger_kg + m_luggage_kg) * kg_to_lb
W_crew = (n_pilots + n_attendants) * (m_crew_kg + m_luggage_kg) * kg_to_lb

# 2) Fuel fractions
R_nmi     = 9150
E_hr      = 0.5
c_tsfc    = 0.52
LD_cruise = 18 * 0.94
V_ms      = 251
V_kt      = V_ms * 1.9438444924

Wf_Wi_cruise = math.exp(-R_nmi * c_tsfc / (V_kt * LD_cruise))
Wf_Wi_loiter = math.exp(-E_hr * c_tsfc / LD_cruise)

segment_fracs = {
    "Takeoff": 0.970,
    "Climb":   0.985,
    "Descent": 0.990,
    "Landing": 0.995
}

W_end_W0 = 1.0
for _, frac in segment_fracs.items():
    W_end_W0 *= frac
W_end_W0 *= Wf_Wi_cruise
W_end_W0 *= Wf_Wi_loiter

fuel_frac_mission = 1.0 - W_end_W0
reserve_factor    = 1.06
fuel_frac_total   = reserve_factor * fuel_frac_mission

print(f"W_payload = {W_payload:,.0f} lb")
print(f"W_crew    = {W_crew:,.0f} lb")
print(f"Total fuel fraction (with reserves) = {fuel_frac_total:.4f}")

# 3) TOGW iteration
A = 0.97 
C = -0.06  

error      = 1e-6
max_iter = 100
W0       = 1000000      
delta = 2*error
W0_array = np.array([])
iter_array = np.array([])
i = 0

while delta > error: 
    W0_array = np.append(W0_array, W0)
    iter_array = np.append(iter_array, i)
    We_W0 = A * (W0 ** C)
    denom = 1.0 - We_W0 - fuel_frac_total
    W0_new = (W_payload + W_crew) / denom
    delta = abs(W0_new - W0) / abs(W0_new)
    W0 = W0_new
    i += 1


#for k in range(max_iter):
  #  We_W0 = A * (W0 ** C)
   # denom = 1.0 - We_W0 - fuel_frac_total
   # if denom <= 0:
   #     raise ValueError("Denominator <= 0. Check regression coefficients and fuel fraction.")
   # W0_new = (W_payload + W_crew) / denom
   # rel_change = abs(W0_new - W0) / W0
   # W0 = W0_new
   # if rel_change < error: 
   #     break

We = We_W0 * W0



# 4) Comparison table 
W0_ref = 770000
We_ref = 320000   

WeW0_est = We / W0
WeW0_ref = (We_ref / W0_ref) 


print(f"Estimated TOGW W0 = {W0:,.0f} lb")
print(f"Reference TOGW W0 = {W0_ref:,.0f} lb")
print(f"Estimated empty weight We = {We:,.0f} lb")
print(f"Reference empty weight We = {We_ref:,.0f} lb")
print(f"Estimated empty-weight fraction We/W0 = {WeW0_est:.4f}")
print(f"Reference empty-weight fraction We/W0 = {WeW0_ref:.4f}")
print(f"Empty-weight fraction We/W0 = {We_W0:.4f}")

plt.figure()
plt.plot(iter_array, W0_array, linewidth=2)
plt.xlabel("Iteration")
plt.ylabel("Takeoff Gross Weight W₀ (lb)")
plt.title("TOGW Iterative Convergence")
plt.grid(True)
plt.show()

