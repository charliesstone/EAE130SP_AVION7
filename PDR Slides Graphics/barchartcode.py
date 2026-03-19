import matplotlib.pyplot as plt
import numpy as np

# Aircraft names
planes = ["YF-52 Concept", "F-35 Lightning II", "F/A-18E/F"]

# Data
rd_cost = [27, 2000, 10]  # billions USD (F-35 = 2 trillion = 2000 billion)
unit_cost = [55, 102, 72]  # million USD
gross_weight = [36700, 50000, 47000]  # lb
engines = [1, 1, 2]
thrust = [33500, 43000, 22000]  # lb per engine
wing_area = [400, 460, 500]  # sq ft

metrics = [
    ("R&D Cost (Billion USD)", rd_cost),
    ("Unit Flyaway Cost (Million USD)", unit_cost),
    ("Gross Weight (lb)", gross_weight),
    ("Number of Engines", engines),
    ("Thrust per Engine (lb)", thrust),
    ("Wing Area (sq ft)", wing_area)
]


fig, axes = plt.subplots(3, 2, figsize=(14, 14))
axes = axes.flatten()

fig.subplots_adjust(hspace=0.5, wspace=0.35)

for i, (ax, (title, values)) in enumerate(zip(axes, metrics)):
    ax.bar(planes, values, color="#4472C4", edgecolor="#2F5597", linewidth=1.2)
    ax.set_title(title)
    ax.set_ylabel(title)
    ax.tick_params(axis='x', labelrotation=20)

    # Limit R&D chart
    if i == 0:
        ax.set_ylim(0, 50)

plt.tight_layout(pad=3)
plt.show()