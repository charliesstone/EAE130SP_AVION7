import numpy as np 
#Weight estimation, componentwise. 

V_i = 1600 #gal, integral fuel tank volume, estimated
V_t = 1694 #Total fuel capacity 
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

#Weight of fuel 
W_fuel = 2.405*(V_t**0.606)*(1+V_i/V_t)**(-1) * (1+V_p/V_t)*N_t**0.05

#Cooling Oil
W_oil = 37.82*N_t**1.023

#Pneumatics
W_pneumatic = 49.19 * (N_t*W_en/1000)**0.541

#Hydraulics
W_hydraulics = 0.001*W_dg

#Electrical
W_electrical = 172.2*K_mc*(R_kva**0.152) *( N_c**0.1) * (L_a**0.1) * (N_gen**0.091)


