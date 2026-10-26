"""Phase 3E-7.6B: KLayout GDS integration for endpoint-constrained Euler routing.

Run from repository root: klayout -b -r tests/test_euler_endpoint_klayout.py
No modification to the existing router. Units are micrometers.
"""
import csv
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pya
from photonics.routing.euler_endpoint_solver import route_straight_euler_straight

OUT = os.path.join(ROOT, 'tests', 'phase3e76b_output')
WIDTH = 0.5
RADIUS = 6.25
POS_TOL = 0.01
HEAD_TOL = 0.1
# Axis-aligned obstacle rectangles (xmin, ymin, xmax, ymax), in um.
CLEAR_OBSTACLES = [(14.0, 7.0, 19.0, 11.0)]
BLOCKING_OBSTACLES = [(15.0, -1.0, 18.0, 1.0)]


def segment_intersects_rect(a, b, rect):
    """Liang-Barsky exact line segment / closed rectangle intersection."""
    xmin, ymin, xmax, ymax = rect
    x0, y0 = a
    dx, dy = b[0] - x0, b[1] - y0
    p = (-dx, dx, -dy, dy)
    q = (x0 - xmin, xmax - x0, y0 - ymin, ymax - y0)
    lo, hi = 0.0, 1.0
    for pi, qi in zip(p, q):
        if abs(pi) < 1e-15:
            if qi < 0:
                return False
        else:
            t = qi / pi
            if pi < 0:
                lo = max(lo, t)
            else:
                hi = min(hi, t)
            if lo > hi:
                return False
    return True


def obstacle_clear(points, obstacles, margin):
    """Conservative check against rectangles expanded by WG half-width + margin.

    It checks the sampled centerline segments, not arbitrary curved boundaries.
    """
    for rect in obstacles:
        xmin, ymin, xmax, ymax = rect
        expanded = (xmin - margin, ymin - margin, xmax + margin, ymax + margin)
        for a, b in zip(points, points[1:]):
            if segment_intersects_rect(a, b, expanded):
                return False
    return True


def tangent_deg(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def angular_error(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def sampled_radius(points):
    """3-point circumradius, ignoring collinear triples."""
    result = []
    for a, b, c in zip(points, points[1:], points[2:]):
        ab = math.dist(a, b)
        bc = math.dist(b, c)
        ac = math.dist(a, c)
        twice_area = abs((b[0] - a[0]) * (c[1] - a[1]) -
                         (b[1] - a[1]) * (c[0] - a[0]))
        if min(ab, bc, ac) < 1e-9 or twice_area < 1e-12:
            continue
        result.append(ab * bc * ac / (2.0 * twice_area))
    return min(result) if result else math.inf


def add_waveguide(layout, cell, layer, points, width):
    cell.shapes(layer).insert(pya.DPath([pya.DPoint(x, y) for x, y in points], width))


def add_obstacles(cell, layer, rects):
    for x0, y0, x1, y1 in rects:
        cell.shapes(layer).insert(pya.DBox(x0, y0, x1, y1))


def main():
    os.makedirs(OUT, exist_ok=True)
    source, destination = (0.0, 0.0), (40.0, 40.0)
    result = route_straight_euler_straight(
        source, destination, 0.0, 90.0, min_radius_um=RADIUS, samples=801,
        position_tolerance_um=POS_TOL, heading_tolerance_deg=HEAD_TOL)
    assert result.valid, 'Solver failed: ' + result.reason
    assert result.points, 'No path points'
    assert math.dist(result.points[0], source) <= POS_TOL
    assert math.dist(result.points[-1], destination) <= POS_TOL
    start_err = angular_error(tangent_deg(result.points[0], result.points[1]), 0.0)
    end_err = angular_error(tangent_deg(result.points[-2], result.points[-1]), 90.0)
    assert start_err <= HEAD_TOL, 'Start sampled heading error too large'
    assert end_err <= HEAD_TOL, 'End sampled heading error too large'
    radius = sampled_radius(result.points)
    # 3-point sampling can have numerical error at Euler/straight junctions.
    assert radius >= RADIUS - 0.05, 'Sampled radius below allowed tolerance'
    margin = WIDTH / 2.0
    assert obstacle_clear(result.points, CLEAR_OBSTACLES, margin), 'Unexpected collision'
    assert not obstacle_clear(result.points, BLOCKING_OBSTACLES, margin), 'Blocking obstacle not detected'

    layout = pya.Layout()
    layout.dbu = 0.001
    cell = layout.create_cell('EULER_ENDPOINT_3E76B')
    wg_layer = layout.layer(1, 0)
    obstacle_layer = layout.layer(90, 0)
    pin_layer = layout.layer(2, 0)
    add_waveguide(layout, cell, wg_layer, result.points, WIDTH)
    add_obstacles(cell, obstacle_layer, CLEAR_OBSTACLES)
    for x, y in (source, destination):
        cell.shapes(pin_layer).insert(pya.DBox(x - 0.25, y - 0.25, x + 0.25, y + 0.25))
    gds = os.path.join(OUT, 'euler_endpoint_90deg.gds')
    layout.write(gds)

    csv_file = os.path.join(OUT, 'euler_endpoint_points.csv')
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['index', 'x_um', 'y_um'])
        for i, (x, y) in enumerate(result.points):
            writer.writerow([i, '%.9f' % x, '%.9f' % y])

    print('Route valid:', result.valid)
    print('Lead lengths (um): %.6f, %.6f' % (result.source_lead_um, result.destination_lead_um))
    print('Route length (um): %.6f' % result.length_um)
    print('Endpoint error (um): %.9f' % result.endpoint_error_um)
    print('Solver heading error (deg): %.9f' % result.heading_error_deg)
    print('Sampled endpoint heading errors (deg): %.6f, %.6f' % (start_err, end_err))
    print('Minimum sampled radius (um): %.6f' % radius)
    print('Clear obstacle: PASS; Blocking obstacle rejected: PASS')
    print('GDS:', gds)
    print('CSV:', csv_file)
    print('Phase 3E-7.6B KLayout integration: PASS')


if __name__ == '__main__':
    main()
