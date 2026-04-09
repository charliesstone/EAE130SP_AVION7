import math

Kcb = 1.0
Ktpg = 1.0
Wl = 31000
Ngear = 4.0
Nl = Ngear * 1.5
Lm = 4.55 * 12
Ln = 4.55 * 12
Nnw = 2

Wmainlg = Kcb * Ktpg * (Wl * Nl) ** 0.25 * Lm ** 0.973
Wnoselg = (Wl * Nl) ** 0.290 * Ln ** 0.5 * Nnw ** 0.525

Wtotlg = 2 * Wmainlg + Wnoselg

print(f"Total Landing Gear Weight: {Wtotlg:.3f} lb")

# Strut geometry
length_ft = 4.55

main_diameter_ft = 5.0 / 12
nose_diameter_ft = 3.5 / 12

# Wheel geometry
main_wheel_diameter_ft = 29.867 / 12
main_wheel_width_ft = 9.141 / 12

nose_wheel_diameter_ft = 22.400 / 12
nose_wheel_width_ft = 6.856 / 12

num_main_struts = 2
num_nose_struts = 1

main_wheels_per_strut = 1
nose_wheels_per_strut = 2

# Correction factors
hollow_factor = 0.6        # struts are hollow
packing_margin = 1.2       # +20% extra space for bay

# -----------------------------
# FUNCTIONS
# -----------------------------

def cylinder_volume(diameter_ft, length_ft):
    r = diameter_ft / 2
    return math.pi * r**2 * length_ft

def weight(volume_ft3, density):
    return volume_ft3 * density

# -----------------------------
# STRUT VOLUMES
# -----------------------------

main_strut_vol_single = cylinder_volume(main_diameter_ft, length_ft)
main_strut_vol_total = main_strut_vol_single * num_main_struts * hollow_factor

nose_strut_vol = cylinder_volume(nose_diameter_ft, length_ft) * hollow_factor

# -----------------------------
# WHEEL VOLUMES
# -----------------------------

main_wheel_vol_single = cylinder_volume(main_wheel_diameter_ft, main_wheel_width_ft)
main_wheel_vol_total = main_wheel_vol_single * num_main_struts * main_wheels_per_strut

nose_wheel_vol_single = cylinder_volume(nose_wheel_diameter_ft, nose_wheel_width_ft)
nose_wheel_vol_total = nose_wheel_vol_single * num_nose_struts * nose_wheels_per_strut

# -----------------------------
# TOTAL VOLUMES
# -----------------------------

total_main_volume = main_strut_vol_total + main_wheel_vol_total
total_nose_volume = nose_strut_vol + nose_wheel_vol_total

total_volume = total_main_volume + total_nose_volume

# Add packaging margin
total_volume_packed = total_volume * packing_margin

print(f"Total volume:      {total_volume:.3f} ft^3")
print(f"Total bay volume (including margins):  {total_volume_packed:.3f} ft^3")