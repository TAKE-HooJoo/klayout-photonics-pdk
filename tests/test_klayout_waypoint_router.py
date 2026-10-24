"""Run: klayout -b -r tests/test_klayout_waypoint_router.py"""
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import pya
from photonics.circuit.geometry import Point
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.obstacle_router_v2 import route_with_waypoints, route_region
from photonics.integration.clearance_klayout import check_route_clearance


def main():
    layout = pya.Layout()
    layout.dbu = 0.001
    xs = WaveguideCrossSection('strip', 0.5, 5.0)
    rules = DesignRules(0.4, 0.5, 5.0)
    start, end = Point(0, 0), Point(80, 0)
    args = (start, end, (1, 0), (-1, 0), xs, rules, layout)
    empty = pya.Region()
    direct = route_with_waypoints(*args, empty)
    assert direct.valid and direct.variant == 'STRAIGHT', direct
    print('Unobstructed straight: PASS')

    blocker = pya.Region(pya.DBox(37, -3, 43, 3).to_itype(layout.dbu))
    routed = route_with_waypoints(*args, blocker)
    assert routed.valid and routed.variant == 'WAYPOINT_CSC', routed
    region = route_region(routed.points, xs.width_um, layout)
    passes, _, _ = check_route_clearance(region, blocker, layout, rules)
    assert passes
    assert routed.length_um > 80
    print('Blocked straight waypoint detour: PASS')
    print('Detour length: %.3f um' % routed.length_um)

    wall = pya.Region(pya.DBox(30, -100, 50, 100).to_itype(layout.dbu))
    failed = route_with_waypoints(*args, wall)
    assert not failed.valid and failed.reason == 'NO_CLEAR_WAYPOINT_ROUTE', failed
    print('No clear waypoint candidate: PASS')
    print('Phase 3E-4 KLayout integration: PASS')


if __name__ == '__main__':
    main()
