"""KLayout batch integration test for hierarchical waveguide obstacle extraction.

Run: klayout -b -r tests/test_klayout_obstacles.py
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pya
from photonics.integration.obstacles_klayout import extract_waveguide_obstacles


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    layout = pya.Layout()
    layout.dbu = 0.001
    waveguide = layout.layer(pya.LayerInfo(1, 0))
    pin = layout.layer(pya.LayerInfo(2, 0))
    top = layout.create_cell('TOP')
    child = layout.create_cell('STRAIGHT_TEST')
    child.shapes(waveguide).insert(pya.DBox(0, -0.25, 10, 0.25))
    child.shapes(pin).insert(pya.DBox(-0.1, -0.1, 0.1, 0.1))
    top.insert(pya.DCellInstArray(child.cell_index(), pya.DTrans(pya.DVector(20, 30))))

    obstacles = extract_waveguide_obstacles(top, layout)
    check(obstacles is not None, 'Extractor returned None')
    check(len(obstacles) == 1, 'Expected 1 hierarchical waveguide obstacle, got %d' % len(obstacles))
    obs = obstacles[0]
    for field, expected in [('xmin', 20.0), ('ymin', 29.75), ('xmax', 30.0), ('ymax', 30.25)]:
        actual = getattr(obs, field, None)
        check(actual is not None, 'Obstacle lacks field %s; inspect dataclass definition' % field)
        check(abs(actual - expected) < 0.002, '%s: expected %s, got %s' % (field, expected, actual))
    print('Hierarchical waveguide extraction: PASS')
    print('Optical pin layer excluded: PASS')
    print('Phase 3E-1 KLayout integration: PASS')


if __name__ == '__main__':
    main()
