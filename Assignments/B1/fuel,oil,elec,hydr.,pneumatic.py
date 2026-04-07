import numpy as np 
#Weight estimation, componentwise. 

V_i = 1600 #gal, integral fuel tank volume, estimated
V_t = 1640 #Total fuel capacity 
V_p = 1600 #gal, protected volume. 
N_t = 3    #Number of tanks
N_en = 1   #Number of engines
W_en = 5000 #lbs
W_dg = 36700 #lbs
L_a = 30    #ft, electrical routing distance, estimated.
N_gen = N_en 
K_mc = 1.45
R_kva = 130  
N_c = 2     #2 crew members
SFC  = 1.9 #maximum thrust 
T = 33500 #lb
#Weight of fuel 
W_fuelSys = (7.45
          *(V_t**0.47)*(1+V_i/V_t)**(-0.095) 
          *(1+V_p/V_t)*(N_t**0.066)*(N_en**0.052)
          *(T*SFC/1000)**0.249 )

#Cooling Oil
W_oil = 37.82*N_t**1.023

#Pneumatics
W_pneumatic = 49.19 * (N_t*W_en/1000)**0.541

#Hydraulics
W_hydraulics = 0.001*W_dg

#Electrical
W_electrical = 172.2*K_mc*(R_kva**0.152) *( N_c**0.1) * (L_a**0.1) * (N_gen**0.091)

W_tot = W_electrical + W_fuelSys + W_hydraulics +W_oil +W_pneumatic
print(f"Electrical Weight = {W_electrical :.2f} lb ")
print(f"Hydraulics' Weight = {W_hydraulics :.2f} lb")
print(f"Pneumatics Wight = {W_pneumatic:.2f}lb")
print(f"Oil Weight = {W_oil :.2f} lb")
print(f"Fuel Systems' Weight = {W_fuelSys :.2f} lb")
print(f"Total: Electrical, Oil, Fuel, Hydraulics and Pneumatics = {W_tot: .2f} lb")
