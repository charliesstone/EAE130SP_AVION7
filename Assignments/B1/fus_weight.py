def fuselage_weight(Kdwf, Wdg, Nz, L, D, W):
    return 0.499 * Kdwf * (Wdg ** 0.35) * (Nz ** 0.25) * (L ** 0.5) * (D ** 0.849) * (W ** 0.685)

Kdwf = 1.0
Wdg = 36700.0
Nz = 12.0
# dimensions from a5_geom1.vsp3
# values may change once we get charlie's most recent vsp file 
L = 40.3604
D = 5.5
W = 5.0

W_fuselage = fuselage_weight(Kdwf, Wdg, Nz, L, D, W)
print(f"Fuselage structural weight = {W_fuselage:.2f} lb")