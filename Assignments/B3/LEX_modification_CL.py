import numpy as np
import matplotlib.pyplot as plt

# --- Inputs ---
S_ref = 400.0  
b = 36.306  # Total span
taper_ratio = 0.69
Lambda = 35.0
cos_Lambda = np.cos(np.radians(Lambda))

CL_base = 1.2
delta_CL_flaps = 0.6  # Constant TE contribution

# Solving for c_root based on S_ref
c_root = (2 * S_ref) / (b * (1 + taper_ratio))

def get_chord(y):
    return c_root * (1 - (2 * (1 - taper_ratio) / b) * y)

def get_segment_area(y1, y2):
    return (y2 - y1) * (get_chord(y1) + get_chord(y2)) / 2

# Sweep LEX Span (y1 for slats)
b_LEX_range = np.linspace(2.46, 12.0, 50)
slat_effectiveness = [0.2, 0.3, 0.4]

plt.figure(figsize=(10, 6))

for dcl in slat_effectiveness:
    cl_max_vals = []
    for b_LEX in b_LEX_range:
        # Slats go from LEX edge (b_LEX) to the tip (b/2)
        S_flapped_slat = get_segment_area(b_LEX, b/2)
        delta_CL_slat_3D = dcl * (S_flapped_slat / S_ref) * cos_Lambda
        cl_max_vals.append(CL_base + delta_CL_flaps + delta_CL_slat_3D)
    
    plt.plot(b_LEX_range, cl_max_vals, label=f'$\Delta c_{{l,slat}} = {dcl}$')

plt.title('Trade Study: LERX Span vs. Landing $C_{L_{max}}$')
plt.xlabel('LERX Spanwise Limit ($b_{LEX}$) [ft]')
plt.ylabel('Total Landing $C_{L_{max}}$')
plt.axvline(x=8.55, color='red', linestyle='--', label='Current Design')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()