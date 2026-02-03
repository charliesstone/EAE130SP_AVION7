import numpy as np
import matplotlib.pyplot as plt

## ------ EAE 130A, preliminary design sizing ------ ##
## ------ Team 7 Avion: Mostafa Hashem, Charlie Stone, Jose Hernandez Negrete, ------ ##
## ------ Valeria Cecena, Quinn Kennerly, Lena Pattamadilok ------ ##

#region input parameters
g = 32.174 #ft/s^2, gravitational acceleration
tar_togw = 50,000 #lbf, target gross take off weight
S_i = 600 #ft^2, initial wing area assumption including strakes (LERX)
S_ialt = 400 #ft^2, initial wing area assumption not including strakes (LERX)
C_D0 = 0.01755 #initial zero-lift drag estimation, from OpenVSP, see:
#(https://github.com/charliesstone/EAE130SP_AVION7/blob/main/Assignments/A2/Concepts/concept_1_COYOTE.vsp3)
e = 0.8 #oswald efficiency factor for fighters, from raymond textbook
nz_tar = 7.0 * g #ft/s^2, load factor, minimum targeted
nz_idl = 8.0 * g #ft/s^2, load factor, ideal targeted




