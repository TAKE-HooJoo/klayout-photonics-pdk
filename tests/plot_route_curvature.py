import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

base = Path("tests/phase3e72_output")
rows = list(csv.DictReader(open(base / "route_curvature.csv")))

s = []
k = []

for row in rows:
    if row["signed_curvature_per_um"]:
        s.append(float(row["distance_um"]))
        k.append(float(row["signed_curvature_per_um"]))

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(s, k, linewidth=1.5)
ax.axhline(0, linewidth=0.8, linestyle="--")
ax.set_xlabel("Distance along route (um)")
ax.set_ylabel("Signed curvature (1/um)")
ax.set_title("Phase 3E-7.3: WAYPOINT_CSC Curvature Profile")
ax.grid(True, alpha=0.3)

fig.tight_layout()
output = base / "route_curvature.png"
fig.savefig(output, dpi=160)
plt.close(fig)

print("Samples:", len(s))
print("Curvature min/max:", min(k), max(k))
print("Saved:", output)
