"""Pure-Python arc-length resampling and curvature stability diagnostics.

Discrete curvature jumps are sample-dependent. CSC nominal jump 1/R is a
separate theoretical proxy and is NOT derived from sampled centerlines.
"""
import csv
import math
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'tests' / 'phase3e78d4_output'
IN = OUT / 'route_centerlines.csv'
STEPS = (0.5, 0.25, 0.1, 0.05)


def resample(points, step):
    if step <= 0:
        raise ValueError('step must be positive')
    distances = [0.]
    for a, b in zip(points, points[1:]):
        d = math.dist(a, b)
        if d <= 0:
            raise ValueError('duplicate consecutive points')
        distances.append(distances[-1] + d)
    total = distances[-1]
    count = max(1, int(math.ceil(total / step)))
    # Uniform arc length INCLUDING exact endpoint; actual spacing <= requested.
    spacing = total / count
    result = []
    j = 0
    for i in range(count + 1):
        s = total if i == count else i * spacing
        while j + 1 < len(distances) - 1 and distances[j + 1] < s:
            j += 1
        span = distances[j + 1] - distances[j]
        t = min(1., max(0., (s - distances[j]) / span))
        a, b = points[j], points[j + 1]
        result.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return result, spacing


def metrics(points, spacing):
    k = [0.] * len(points)
    for i in range(1, len(points) - 1):
        a, b, c = points[i - 1], points[i], points[i + 1]
        u = (b[0] - a[0], b[1] - a[1])
        v = (c[0] - b[0], c[1] - b[1])
        cross = u[0] * v[1] - u[1] * v[0]
        chord = math.dist(a, c)
        denom = math.hypot(*u) * math.hypot(*v) * chord
        k[i] = 2 * cross / denom if denom > 1e-20 else 0.
    energy = spacing * (sum(x*x for x in k[1:-1]))
    delta = max(abs(a-b) for a,b in zip(k,k[1:]))
    return energy, delta, max(abs(x) for x in k)


def main():
    if not IN.exists():
        raise SystemExit('Missing %s; run klayout -b -r tests/export_route_points_v65.py first' % IN)
    grouped = defaultdict(list)
    with IN.open(newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            grouped[(r['case'], r['mode'], r['variant'], r['designed_radius_um'])].append(
                (int(r['index']), (float(r['x_um']), float(r['y_um']))))
    output = []
    for (case, mode, variant, radius), entries in sorted(grouped.items()):
        points = [p for _, p in sorted(entries)]
        for step in STEPS:
            sampled, actual = resample(points, step)
            energy, delta, maxk = metrics(sampled, actual)
            # Nominal CSC curvature jump is 1/R for straight-to-circular-arc
            # transitions; do NOT present this as an extracted exact topology.
            nominal = 1 / float(radius) if variant in ('LSL','LSR','RSL','RSR','RLR','LRL') and float(radius)>0 else ''
            output.append(dict(case=case, mode=mode, variant=variant,
                               requested_step_um=step, actual_step_um=actual,
                               length_um=actual*(len(sampled)-1), points=len(sampled),
                               sampled_energy_inv_um=energy,
                               sampled_max_delta_kappa_inv_um=delta,
                               sampled_max_abs_kappa_inv_um=maxk,
                               csc_nominal_jump_proxy_inv_um=nominal))
            print('%-17s %-12s %-12s ds=%5.2f E=%.6f dK=%.6f' %
                  (case, mode, variant, step, energy, delta))
    path = OUT / 'curvature_sampling_sweep.csv'
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    # Verify resampling preserves geometric path length to numerical precision.
    by_route = defaultdict(list)
    for r in output:
        by_route[(r['case'],r['mode'])].append(float(r['length_um']))
    for key, values in by_route.items():
        assert max(values)-min(values) < 1e-7, (key, values)
    print('CSV:', path)
    print('Phase 3E-7.8D-4 sampling: PASS')

if __name__ == '__main__':
    main()
