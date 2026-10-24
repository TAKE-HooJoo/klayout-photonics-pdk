"""Run: klayout -b -r tests/test_klayout_obstacle_router.py"""
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pya
from photonics.circuit.geometry import Point
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.obstacle_router import route_avoiding_obstacles, route_region


def main():
    layout = pya.Layout()
    layout.dbu = 0.001
    xs = WaveguideCrossSection('strip', 0.5, 5.0)
    rules = DesignRules(0.4, 0.5, 5.0)
    empty = pya.Region()
    start, end = Point(0, 0), Point(30, 0)
    args = (start, end, (1, 0), (-1, 0), xs, rules, layout)

    clear = route_avoiding_obstacles(*args, empty)
    assert clear.valid and clear.variant == 'STRAIGHT', clear
    print('Clear straight route: PASS')

    blocker = pya.Region(pya.DBox(14, -2, 16, 2).to_itype(layout.dbu))
    blocked = route_avoiding_obstacles(*args, blocker)
    assert not blocked.valid and blocked.reason == 'ALL_CANDIDATES_BLOCKED', blocked
    print('Blocked straight route: PASS')

    # A curved connection: at least one candidate is legal without obstacles.
    curve_args = (Point(0, 0), Point(30, 15), (1, 0), (-1, 0), xs, rules, layout)
    curved = route_avoiding_obstacles(*curve_args, empty)
    assert curved.valid and curved.variant in ('LSL', 'RSR', 'LSR', 'RSL'), curved
    assert not route_region(curved.points, xs.width_um, layout).is_empty()
    print('CSC route and Region: PASS')

    print('Phase 3E-3 KLayout integration: PASS')


if __name__ == '__main__':
    main()
