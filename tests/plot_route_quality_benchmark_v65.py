"""Phase 3E-7.8D-2: plot the 7.8D-1 benchmark CSV (standard Python)."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / 'tests/phase3e78d1_output/route_quality_benchmark.csv'
OUT = ROOT / 'tests/phase3e78d2_output'
MODES = ('AUTO', 'CSC', 'EULER', 'AUTO_QUALITY')
METRICS = (
    ('length_um', 'Route length (um)', 'length'),
    ('curvature_energy_inv_um', 'Sampled curvature energy (1/um)', 'curvature_energy'),
    ('max_delta_curvature_inv_um', 'Max sampled delta curvature (1/um)', 'delta_curvature'),
    ('relative_score', 'Benchmark relative score (dimensionless)', 'relative_score'),
)

def main():
    if not CSV.exists():
        raise SystemExit('Missing input CSV: ' + str(CSV))
    with CSV.open(newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit('Empty CSV')
    OUT.mkdir(parents=True, exist_ok=True)
    cases = list(dict.fromkeys(r['case'] for r in rows))
    for case in cases:
        subset = {r['mode']: r for r in rows if r['case'] == case}
        for key, ylabel, suffix in METRICS:
            valid = [(m, float(subset[m][key])) for m in MODES if m in subset and subset[m]['valid'].lower() == 'true' and subset[m].get(key)]
            if not valid:
                continue
            fig, ax = plt.subplots(figsize=(8, 4.6))
            bars = ax.bar([m for m, _ in valid], [v for _, v in valid])
            ax.set_ylabel(ylabel)
            ax.set_title(case + ' — ' + suffix.replace('_', ' '))
            ax.grid(axis='y', alpha=.25)
            ax.set_axisbelow(True)
            ax.tick_params(axis='x', labelrotation=12)
            for bar, (_, value) in zip(bars, valid):
                ax.annotate(f'{value:.5g}', (bar.get_x()+bar.get_width()/2, bar.get_height()),
                            ha='center', va='bottom', fontsize=9, xytext=(0, 3), textcoords='offset points')
            ax.set_ylim(0, max(v for _, v in valid)*1.17 if max(v for _, v in valid)>0 else 1)
            fig.tight_layout()
            target = OUT / f'{case}_{suffix}.png'
            fig.savefig(target, dpi=170)
            plt.close(fig)
            print('PNG:', target)
        for mode in MODES:
            r = subset.get(mode)
            if r and r['valid'].lower() != 'true':
                print('INVALID:', case, mode, r['reason'])
    print('Phase 3E-7.8D-2 CSV metric plots: PASS')
    print('NOTE: CSV contains aggregate metrics only; kappa(s) plots require route point samples.')

if __name__ == '__main__':
    main()
