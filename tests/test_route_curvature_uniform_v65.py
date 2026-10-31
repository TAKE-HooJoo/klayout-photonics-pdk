"""Phase 3E-7.8B: equal-arclength curvature diagnostics.
Run: klayout -b -r tests/test_route_curvature_uniform_v65.py
Only standard library, pya, and existing photonics modules are needed.
"""
import csv
import math
import os
import sys
from bisect import bisect_right
from dataclasses import dataclass

sys.path.insert(0, os.getcwd())
import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.router_hybrid_v65 import route_between_ports_hybrid

STEP_UM = 0.1
OUT = os.path.join(os.getcwd(), 'tests', 'phase3e78b_output')
os.makedirs(OUT, exist_ok=True)

@dataclass
class Port:
    position: object
    direction: tuple
    width: float = 0.5


def uniform_sample(points, step):
    xy = [(float(p.x), float(p.y)) for p in points]
    clean = [xy[0]]
    for p in xy[1:]:
        if math.dist(p, clean[-1]) > 1e-10:
            clean.append(p)
    assert len(clean) >= 2
    arclength = [0.0]
    for a, b in zip(clean, clean[1:]):
        arclength.append(arclength[-1] + math.dist(a, b))
    total = arclength[-1]
    assert total > 0
    n = max(1, int(math.ceil(total / step)))
    ss = [min(i * step, total) for i in range(n)] + [total]
    result = []
    for s in ss:
        j = min(bisect_right(arclength, s) - 1, len(clean) - 2)
        ds = arclength[j + 1] - arclength[j]
        t = (s - arclength[j]) / ds
        a, b = clean[j], clean[j + 1]
        result.append((s, a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return result


def signed_curvature(a, b, c):
    ax, ay = a[1], a[2]
    bx, by = b[1], b[2]
    cx, cy = c[1], c[2]
    ab = math.hypot(bx-ax, by-ay)
    bc = math.hypot(cx-bx, cy-by)
    ac = math.hypot(cx-ax, cy-ay)
    if min(ab, bc, ac) < 1e-12:
        return 0.0
    cross = (bx-ax)*(cy-ay)-(by-ay)*(cx-ax)
    return 2.0*cross/(ab*bc*ac)


def curvature_rows(samples):
    rows = []
    for i, (s, x, y) in enumerate(samples):
        k = None if i == 0 or i == len(samples)-1 else signed_curvature(samples[i-1], samples[i], samples[i+1])
        rows.append({'s_um': s, 'x_um': x, 'y_um': y, 'kappa_per_um': k})
    return rows


def write_csv(path, rows, fields):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({key: ('' if row[key] is None else row[key]) for key in fields})


def main():
    xs = WaveguideCrossSection('strip', 0.5, 6.25)
    rules = DesignRules(0.4, 0.5, 6.25)
    src = Port(pya.DPoint(0, 0), (1.0, 0.0))
    dst = Port(pya.DPoint(80, 15), (-1.0, 0.0))
    summary = []
    for mode, expected in [('AUTO', 'EULER_SBEND'), ('CSC', None)]:
        ly = pya.Layout()
        ly.dbu = 0.001
        cell = ly.create_cell('CURVATURE_' + mode)
        r = route_between_ports_hybrid(cell, ly, src, dst, xs, rules, mode=mode)
        assert r.valid, '%s failed: %s' % (mode, r.reason)
        if expected:
            assert r.variant == expected, (mode, r.variant)
        samples = uniform_sample(r.points, STEP_UM)
        rows = curvature_rows(samples)
        kappas = [row['kappa_per_um'] for row in rows if row['kappa_per_um'] is not None]
        diffs = [abs(b-a) for a, b in zip(kappas, kappas[1:])]
        max_k = max(abs(k) for k in kappas)
        max_delta = max(diffs) if diffs else 0.0
        # Curvature discontinuity is assessed as a sampled diagnostic only.
        summary.append(dict(mode=mode, variant=r.variant, length_um=r.length_um,
                            sampled_polyline_um=samples[-1][0], sample_step_um=STEP_UM,
                            sample_count=len(samples), max_abs_kappa_per_um=max_k,
                            max_adjacent_delta_kappa_per_um=max_delta))
        write_csv(os.path.join(OUT, mode.lower() + '_uniform_curvature.csv'), rows,
                  ['s_um', 'x_um', 'y_um', 'kappa_per_um'])
        ly.write(os.path.join(OUT, mode.lower() + '.gds'))
        print('%s: variant=%s length=%.6f samples=%d max|k|=%.6f max|delta_k|=%.6f' %
              (mode, r.variant, r.length_um, len(samples), max_k, max_delta))
    write_csv(os.path.join(OUT, 'summary.csv'), summary,
              ['mode', 'variant', 'length_um', 'sampled_polyline_um', 'sample_step_um',
               'sample_count', 'max_abs_kappa_per_um', 'max_adjacent_delta_kappa_per_um'])
    print('Phase 3E-7.8B uniform arclength curvature: PASS')
    print('Output:', OUT)

if __name__ == '__main__':
    main()
