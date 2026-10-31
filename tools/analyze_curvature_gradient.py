"""Phase 3E-7.8D-6: fixed-window gradient and declared CSC jump diagnostic."""
import argparse
import csv
import importlib.util
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D5 = ROOT / 'tools/analyze_curvature_window.py'
DEFAULT_IN = ROOT / 'tests/phase3e78d4_output/route_centerlines.csv'
DEFAULT_OUT = ROOT / 'tests/phase3e78d6_output'


def load_d5(path=D5):
    if not path.exists():
        raise FileNotFoundError('D-5 tool missing: %s (install Phase 3E-7.8D-5 first)' % path)
    spec = importlib.util.spec_from_file_location('curvature_window_d5', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def declared_jump(variant, radius):
    """Ideal line/circle CSC jump magnitude; not inferred from polygon samples.

    Returns None for all non-CSC or unrecognized topologies. For LSR,
    a line-to-arc transition has magnitude 1/R; actual boundaries and
    continuity must be verified from analytic route metadata.
    """
    if variant not in ('LSL', 'RSR', 'LSR', 'RSL'):
        return None
    if not math.isfinite(radius) or radius <= 0:
        return None
    return 1.0 / radius


def evaluate(d5, points, step, half_window):
    data = d5.evaluate(points, step, half_window)
    s = d5.prepare(points)
    n = data['evaluation_points'] - 1
    ds = data['actual_step_um']
    ks = [d5.window_curvature(points, s, half_window + i*ds, half_window)
          for i in range(n+1)]
    gradients = [(b-a)/ds for a,b in zip(ks, ks[1:])]
    data['max_abs_window_gradient_inv_um2'] = max(map(abs, gradients), default=0.0)
    data['rms_window_gradient_inv_um2'] = math.sqrt(
        sum(g*g for g in gradients)/len(gradients)) if gradients else 0.0
    return data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, default=DEFAULT_IN)
    p.add_argument('--output', type=Path, default=DEFAULT_OUT)
    p.add_argument('--half-window', type=float, default=1.0)
    p.add_argument('--steps', type=float, nargs='+', default=[0.5, 0.25, 0.1, 0.05])
    a = p.parse_args()
    if not a.input.exists():
        p.error('missing route CSV: %s; run D-4 export first' % a.input)
    if a.half_window <= 0 or any(v <= 0 for v in a.steps):
        p.error('window and steps must be positive')
    d5 = load_d5()
    rows = []
    for key, points in sorted(d5.load(a.input).items()):
        case, mode, variant, radius_text = key
        radius = float(radius_text)
        jump = declared_jump(variant, radius)
        for step in a.steps:
            metrics = evaluate(d5, points, step, a.half_window)
            row = dict(case=case, mode=mode, variant=variant,
                       designed_radius_um=radius, requested_step_um=step,
                       window_energy_inv_um=metrics['window_energy_inv_um'],
                       actual_step_um=metrics['actual_step_um'],
                       max_abs_window_gradient_inv_um2=metrics['max_abs_window_gradient_inv_um2'],
                       rms_window_gradient_inv_um2=metrics['rms_window_gradient_inv_um2'],
                       ideal_csc_line_arc_jump_inv_um='' if jump is None else jump,
                       jump_source='ideal_CSC_topology' if jump is not None else 'unknown_not_zero')
            rows.append(row)
            print('%-17s %-12s %-12s ds=%5.2f Gmax=%10.6f Jr=%s' % (
                case, mode, variant, step, row['max_abs_window_gradient_inv_um2'],
                ('%.6f' % jump) if jump is not None else 'N/A'))
    if not rows:
        p.error('no valid routes found in CSV')
    a.output.mkdir(parents=True, exist_ok=True)
    output = a.output/'curvature_gradient_sweep.csv'
    with output.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print('CSV:', output)
    print('Phase 3E-7.8D-6 gradient analysis: PASS')


if __name__ == '__main__':
    main()
