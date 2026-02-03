import numpy as np
import matplotlib.pyplot as plt

## ------ EAE 130A, preliminary design sizing ------ ##
## ------ Team 7 Avion: Mostafa Hashem, Charlie Stone, Jose Hernandez Negrete, ------ ##
## ------ Valeria Cecena, Quinn Kennerly, Lena Pattamadilok ------ ##

#region inputs
g = 32.174 #ft/s^2, gravitational acceleration
tar_togw = 50,000 #lbf, target gross take off weight
S_i = 600 #ft^2, initial wing area assumption including strakes (LERX)
S_ialt = 400 #ft^2, initial wing area assumption not including strakes (LERX)
C_D0 = 0.01755 #initial zero-lift drag estimation, from OpenVSP, see:
#(https://github.com/charliesstone/EAE130SP_AVION7/blob/main/Assignments/A2/Concepts/concept_1_COYOTE.vsp3)
e = 0.8 #oswald efficiency factor for fighters, from raymond textbook
nz_tar = 7.0 * g #ft/s^2, load factor, minimum targeted
nz_idl = 8.0 * g #ft/s^2, load factor, ideal targeted
wingload = np.linspace(0, 200, 500)
thrustload = np.linspace(0, 2.5, 500)
#endregion

#region stall
Vstall_L = 220 #ft/s (130 KIAS), stall speed for landing (based on F/A-18E/F)
Vstall_C = 195 #ft/s (115 KIAS), stall speed for cruise (based on F/A-18E/F)
Vstall_T = 205 #ft/s (120 KIAS), stall speed for takeoff (based on F/A-18E/F)
rho_30k = 8.91E-4 #slugs/ft^3, atmospheric density at 30k ft
rho_SL = 23.77E-4 #slugs/ft^3, atmospheric density at sea level
CLmax_L = 2.0
CLmax_C = 1.5
CLmax_T = 1.7




