#!/usr/bin/env python3
"""Phase 3E-7.5: independent circular-arc vs symmetric Euler-bend comparison.
Run: klayout -b -r tests/test_euler_vs_csc_klayout.py
"""
import csv
import math
import os
import sys

try:
    import pya
except ImportError:
    from klayout import db as pya

R = 6.25
WIDTH = 0.5
ANGLE = math.pi / 2
N = 800
OUT = os.path.join('tests', 'phase3e75_output')
os.makedirs(OUT, exist_ok=True)

# Circular 90-degree bend: starts at (0,0), heading +X.
arc_length = R * ANGLE
arc = [(R * math.sin(ANGLE * i / N), R * (1 - math.cos(ANGLE * i / N))) for i in range(N + 1)]

# Symmetric Euler bend with linear ramp 0 -> 1/R -> 0.
# Integral of triangular curvature = L/(2R) = ANGLE.
euler_length = 2 * R * ANGLE
h = euler_length / N
x = y = theta = 0.0
euler = [(x, y)]
for i in range(N):
    smid = (i + 0.5) * h
    k = (smid / (R * (euler_length / 2))) if smid <= euler_length / 2 else ((euler_length - smid) / (R * (euler_length / 2)))
    tmid = theta + 0.5 * k * h
    x += h * math.cos(tmid)
    y += h * math.sin(tmid)
    theta += k * h
    euler.append((x, y))

def profile(points, length, kind):
    rows = []
    for i, (px, py) in enumerate(points):
        s = length * i / N
        if kind == 'CSC_arc':
            k = 1 / R
        else:
            k = (s / (R * (length / 2))) if s <= length / 2 else ((length - s) / (R * (length / 2)))
        rows.append((kind, i, s, px, py, k, (1 / k if k > 1e-12 else '')))
    return rows

layout = pya.Layout()
layout.dbu = 0.001
cell = layout.create_cell('EULER_VS_CSC_90DEG')
layer_arc = layout.layer(1, 0)
layer_euler = layout.layer(3, 0)
layer_text = layout.layer(10, 0)

def add_waveguide(points, layer, dy):
    pts = [pya.DPoint(px, py + dy) for px, py in points]
    path = pya.DPath(pts, WIDTH)
    cell.shapes(layer).insert(path.polygon().to_itype(layout.dbu))

add_waveguide(arc, layer_arc, 0)
add_waveguide(euler, layer_euler, 30)
cell.shapes(layer_text).insert(pya.DText('Circular 90 deg, Rmin=6.25um', pya.DTrans(pya.DVector(0, -4))))
cell.shapes(layer_text).insert(pya.DText('Euler 90 deg, Rmin=6.25um', pya.DTrans(pya.DVector(0, 26))))

gds = os.path.join(OUT, 'euler_vs_csc_90deg.gds')
layout.write(gds)

csv_path = os.path.join(OUT, 'bend_curvature_comparison.csv')
with open(csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['bend', 'index', 'distance_um', 'x_um', 'y_um', 'curvature_per_um', 'radius_um'])
    for row in profile(arc, arc_length, 'CSC_arc') + profile(euler, euler_length, 'Euler'):
        writer.writerow(row)

arc_end = arc[-1]
euler_end = euler[-1]
endpoint_delta = math.hypot(euler_end[0] - arc_end[0], euler_end[1] - arc_end[1])
print('Circular arc length: %.6f um' % arc_length)
print('Euler bend length: %.6f um' % euler_length)
print('Circular endpoint: (%.6f, %.6f) um' % arc_end)
print('Euler endpoint: (%.6f, %.6f) um' % euler_end)
print('Endpoint delta: %.6f um' % endpoint_delta)
print('Euler final heading: %.6f deg' % math.degrees(theta))
print('Minimum design radius: %.6f um' % R)
print('GDS:', os.path.abspath(gds))
print('CSV:', os.path.abspath(csv_path))
assert abs(math.degrees(theta) - 90) < 0.001
assert abs(arc_end[0] - R) < 1e-8
assert abs(arc_end[1] - R) < 1e-8
assert len(euler) == N + 1
print('Phase 3E-7.5 geometry comparison: PASS')
