"""Plot Phase 3E-7.8B CSV output (optional matplotlib dependency)."""
import csv
import os
import matplotlib.pyplot as plt

out = os.path.join('tests', 'phase3e78b_output')
fig, ax = plt.subplots(figsize=(10, 4.5))
for mode, label in [('auto', 'Euler S-Bend (AUTO)'), ('csc', 'CSC')]:
    with open(os.path.join(out, mode + '_uniform_curvature.csv'), newline='') as f:
        rows = list(csv.DictReader(f))
    ss = [float(r['s_um']) for r in rows if r['kappa_per_um']]
    ks = [float(r['kappa_per_um']) for r in rows if r['kappa_per_um']]
    ax.plot(ss, ks, label=label, linewidth=1.3)
ax.set(xlabel='Arc length s (um)', ylabel='Sampled signed curvature kappa (1/um)',
       title='Phase 3E-7.8B: Uniform arclength curvature (0.1 um)')
ax.grid(True, alpha=0.3)
ax.legend()
fig.tight_layout()
path = os.path.join(out, 'curvature_comparison.png')
fig.savefig(path, dpi=170)
print('Saved:', path)
