"""Phase 3E-7.8A: compare AUTO Euler S-bend vs CSC on identical ports.
Run from repository root: klayout -b -r tests/test_route_curvature_compare_v65.py
Outputs CSV and summary; no changes to router or GUI.
"""
import os
import sys
import math
import csv
from dataclasses import dataclass

sys.path.insert(0, os.getcwd())
import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.router_hybrid_v65 import route_between_ports_hybrid

@dataclass
class Port:
    position: object
    direction: tuple
    width: float = 0.5

OUT = os.path.join(os.getcwd(), 'tests', 'phase3e78a_output')
os.makedirs(OUT, exist_ok=True)
xs = WaveguideCrossSection('strip', 0.5, 6.25)
rules = DesignRules(0.4, 0.5, 6.25)
source = Port(pya.DPoint(0, 0), (1.0, 0.0))
destination = Port(pya.DPoint(80, 15), (-1.0, 0.0))


def curvature_samples(points):
    """3-point circumcircle curvature; samples at interior vertices.
    This is a discretization diagnostic, NOT a continuous curvature proof.
    """
    xy = [(float(p.x), float(p.y)) for p in points]
    seg = [math.hypot(xy[i+1][0]-xy[i][0], xy[i+1][1]-xy[i][1])
           for i in range(len(xy)-1)]
    s = [0.0]
    for d in seg:
        s.append(s[-1] + d)
    samples = []
    for i in range(1, len(xy)-1):
        ax, ay = xy[i-1]
        bx, by = xy[i]
        cx, cy = xy[i+1]
        ab, bc = seg[i-1], seg[i]
        ac = math.hypot(cx-ax, cy-ay)
        cross = (bx-ax)*(cy-ay) - (by-ay)*(cx-ax)
        k = 0.0 if ab*bc*ac < 1e-18 else 2.0*cross/(ab*bc*ac)
        samples.append((s[i], k))
    return s[-1], samples


results = {}
for mode in ('AUTO', 'CSC'):
    ly = pya.Layout()
    ly.dbu = 0.001
    cell = ly.create_cell('COMPARE_' + mode)
    wg = ly.layer(pya.LayerInfo(1, 0))
    before = cell.shapes(wg).size()
    r = route_between_ports_hybrid(cell, ly, source, destination, xs, rules,
                                   mode=mode)
    assert r.valid, (mode, r.reason)
    assert cell.shapes(wg).size() == before + 1, 'Expected one inserted geometry'
    polyline_length, profile = curvature_samples(r.points)
    with open(os.path.join(OUT, mode.lower() + '_curvature.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['arc_length_um', 'signed_curvature_per_um'])
        w.writerows(profile)
    ly.write(os.path.join(OUT, mode.lower() + '.gds'))
    kmax = max((abs(k) for _, k in profile), default=0.0)
    # Differences of sampled k are mesh-dependent; not a physical dk/ds metric.
    jump = max((abs(profile[i][1]-profile[i-1][1])
                for i in range(1, len(profile))), default=0.0)
    results[mode] = (r, polyline_length, len(profile), kmax, jump)
    print('%s: variant=%s length=%.6f um polyline=%.6f um '
          'sampled_Rmin=%.6f um max|k|=%.6f 1/um max_delta_k=%.6f 1/um points=%d' %
          (mode, r.variant, r.length_um, polyline_length,
           r.measured_radius_um, kmax, jump, len(r.points)))

assert results['AUTO'][0].variant == 'EULER_SBEND', 'AUTO did not select S-bend'
assert results['CSC'][0].variant != 'EULER_SBEND', 'CSC selected S-bend unexpectedly'
with open(os.path.join(OUT, 'summary.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['mode', 'variant', 'length_um', 'polyline_length_um',
                'sampled_radius_um', 'max_abs_k_per_um',
                'max_neighbor_delta_k_per_um', 'interior_samples'])
    for mode, (r, plen, count, kmax, jump) in results.items():
        w.writerow([mode, r.variant, r.length_um, plen,
                    r.measured_radius_um, kmax, jump, count])
print('Phase 3E-7.8A curvature comparison: PASS')
print('Output:', OUT)
