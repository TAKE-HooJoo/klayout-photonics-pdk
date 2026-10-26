"""Phase 3E-7.2: measure the real Router v6.4 waypoint detour.

Run: klayout -b -r tests/test_route_quality_klayout.py
CSV output: tests/phase3e72_output/route_curvature.csv
"""
import csv
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.router_v64 import route_between_ports_v64
from photonics.routing.route_quality import analyze_route
from photonics.integration.obstacle_router import route_region
from photonics.integration.clearance_klayout import check_route_clearance


class Port:
    def __init__(self, x, y, direction):
        self.position = pya.DPoint(x, y)
        self.direction = direction
        self.width = 0.5


def xy(point):
    return (float(point.x), float(point.y)) if hasattr(point, 'x') else (float(point[0]), float(point[1]))


def main():
    layout = pya.Layout()
    layout.dbu = 0.001
    cell = layout.create_cell('PHASE3E72_QUALITY')
    wg = layout.layer(pya.LayerInfo(1, 0))
    blocker = pya.Region(pya.DBox(37, -3, 43, 3).to_itype(layout.dbu))
    cell.shapes(wg).insert(blocker)
    xs = WaveguideCrossSection('strip', 0.5, 5.0)
    rules = DesignRules(0.4, 0.5, 5.0)
    result = route_between_ports_v64(cell, layout, Port(0, 0, (1, 0)),
                                     Port(80, 0, (-1, 0)), xs, rules)
    assert result.valid, 'Route failed: %s' % result.reason
    assert result.variant == 'WAYPOINT_CSC', result.variant
    report = analyze_route(result.points, min_radius_um=5.0, turn_threshold_deg=5.0)
    routed = route_region(result.points, xs.width_um, layout)
    clear, _, _ = check_route_clearance(routed, blocker, layout, rules)
    assert clear, 'Obstacle clearance regression'
    assert not report.zero_length_segments, report.zero_length_segments
    assert not report.radius_violations, report.radius_violations[:10]
    assert not report.sharp_vertices, report.sharp_vertices[:10]
    assert abs(report.length_um - result.length_um) < 0.02, 'Length mismatch'

    outdir = os.path.join(ROOT, 'tests', 'phase3e72_output')
    os.makedirs(outdir, exist_ok=True)
    outcsv = os.path.join(outdir, 'route_curvature.csv')
    coordinates = [xy(p) for p in result.points]
    cumulative = [0.0]
    for a, b in zip(coordinates, coordinates[1:]):
        cumulative.append(cumulative[-1] + math.hypot(b[0]-a[0], b[1]-a[1]))
    with open(outcsv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['vertex_index', 'distance_um', 'x_um', 'y_um',
                         'signed_curvature_per_um', 'sampled_radius_um'])
        curvature = dict(report.sampled_curvature)
        for i, (x, y) in enumerate(coordinates):
            k = curvature.get(i)
            writer.writerow([i, '%.9f' % cumulative[i], '%.9f' % x, '%.9f' % y,
                             '' if k is None else '%.9f' % k,
                             '' if k is None else ('inf' if k == 0 else '%.9f' % (1.0/abs(k)))])
    print('Variant:', result.variant)
    print('Route length (um): %.3f' % result.length_um)
    print('Points:', report.point_count)
    print('Max sampled turn (deg): %.6f' % report.max_turn_deg)
    print('Min sampled radius (um): %.6f' % report.min_sampled_radius_um)
    print('Max abs curvature (1/um): %.6f' % report.max_abs_curvature_per_um)
    print('Sharp vertices:', report.sharp_vertices)
    print('Radius violations:', report.radius_violations)
    print('Obstacle clearance:', clear)
    print('CSV:', outcsv)
    print('Phase 3E-7.2 real-route quality: PASS')


if __name__ == '__main__':
    main()
