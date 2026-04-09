import math

# -----------------------------
# INPUTS
# -----------------------------

# Strut geometry
length_ft = 4.55

main_diameter_ft = 5.0 / 12
nose_diameter_ft = 3.5 / 12

# Wheel geometry
main_wheel_diameter_ft = 29.867 / 12
main_wheel_width_ft = 9.141 / 12

nose_wheel_diameter_ft = 22.400 / 12
nose_wheel_width_ft = 6.856 / 12

# تعداد (counts)
num_main_struts = 2
num_nose_struts = 1

main_wheels_per_strut = 1
nose_wheels_per_strut = 2

# Material densities (lb/ft^3)
density_steel = 490
density_titanium = 281

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

# -----------------------------
# WEIGHT CALCULATIONS
# -----------------------------

# Only struts contribute significantly to structural weight
main_weight_steel = weight(main_strut_vol_total, density_steel)
nose_weight_steel = weight(nose_strut_vol, density_steel)

main_weight_ti = weight(main_strut_vol_total, density_titanium)
nose_weight_ti = weight(nose_strut_vol, density_titanium)

total_weight_steel = main_weight_steel + nose_weight_steel
total_weight_ti = main_weight_ti + nose_weight_ti

# -----------------------------
# OUTPUT
# -----------------------------

print("========== VOLUMES ==========")

print("\n--- STRUTS ---")
print(f"Main struts total: {main_strut_vol_total:.3f} ft^3")
print(f"Nose strut:        {nose_strut_vol:.3f} ft^3")

print("\n--- WHEELS ---")
print(f"Main wheels total: {main_wheel_vol_total:.3f} ft^3")
print(f"Nose wheels total: {nose_wheel_vol_total:.3f} ft^3")

print("\n--- TOTAL GEAR ---")
print(f"Main gear volume:  {total_main_volume:.3f} ft^3")
print(f"Nose gear volume:  {total_nose_volume:.3f} ft^3")
print(f"Total volume:      {total_volume:.3f} ft^3")

print("\n--- PACKAGED (with margin) ---")
print(f"Total bay volume:  {total_volume_packed:.3f} ft^3")

print("\n========== WEIGHTS ==========")

print("\n--- STEEL ---")
print(f"Main gear: {main_weight_steel:.1f} lb")
print(f"Nose gear: {nose_weight_steel:.1f} lb")
print(f"Total:     {total_weight_steel:.1f} lb")

print("\n--- TITANIUM ---")
print(f"Main gear: {main_weight_ti:.1f} lb")
print(f"Nose gear: {nose_weight_ti:.1f} lb")
print(f"Total:     {total_weight_ti:.1f} lb")
