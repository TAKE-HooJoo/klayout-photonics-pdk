"""Phase 3E-6 KLayout diagnostic smoke test.

Run: klayout -b -r tests/test_router_v64_klayout.py

This test deliberately fails if the router ignores an existing WG polygon.
It checks both actual insertion and clearance; it does not mask adapter bugs.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.router_v64 import route_between_ports_v64
from photonics.integration.clearance_klayout import waveguide_region, check_route_clearance
from photonics.integration.obstacle_router import route_region


class Port:
    def __init__(self, x, y, direction):
        self.position = pya.DPoint(x, y)
        self.direction = direction
        self.width = 0.5


def geometry(cell, layer):
    return pya.Region(cell.begin_shapes_rec(layer)).merged()


def snapshot(cell, layer):
    """Capture immutable numeric values BEFORE routing mutates the layout."""
    region = geometry(cell, layer)
    return cell.shapes(layer).size(), int(region.area()), region.bbox()


def report(label, layout, cell, layer, before, after, result):
    print('=== %s ===' % label)
    print('WG layer:', layout.get_info(layer))
    print('Route valid:', result.valid)
    print('Route variant:', result.variant)
    print('Route reason:', result.reason)
    print('Route length (um): %.3f' % result.length_um)
    print('Route points:', len(result.points))
    print('Direct shapes before/after:', before[0], after[0])
    print('Area before/after (dbu^2):', before[1], after[1])
    print('Area increase (dbu^2):', after[1] - before[1])
    print('Bounding box before:', before[2])
    print('Bounding box after:', after[2])
    print('waveguide_region area:', waveguide_region(cell, layout).area())


def test_obstacle_avoidance():
    ly = pya.Layout()
    ly.dbu = 0.001
    cell = ly.create_cell('ROUTER_V64_TEST')
    wg = ly.layer(pya.LayerInfo(1, 0))
    blocker = pya.Region(pya.DBox(37, -3, 43, 3).to_itype(ly.dbu))
    cell.shapes(wg).insert(blocker)
    xs = WaveguideCrossSection('strip', 0.5, 5.0)
    rules = DesignRules(0.4, 0.5, 5.0)
    a = Port(0, 0, (1, 0))
    b = Port(80, 0, (-1, 0))

    # Key diagnostic: does the adapter's obstacle reader see a WG polygon?
    extracted = waveguide_region(cell, ly)
    print('Blocker area:', blocker.area())
    print('Extracted obstacle area:', extracted.area())
    print('Extracted blocker overlap:', (extracted & blocker).area())

    before = snapshot(cell, wg)
    result = route_between_ports_v64(cell, ly, a, b, xs, rules)
    after = snapshot(cell, wg)
    report('Obstacle avoidance', ly, cell, wg, before, after, result)

    assert result.valid, 'Router rejected route: %s' % result
    assert result.variant == 'WAYPOINT_CSC', result.variant
    assert result.length_um > 80.0, result.length_um
    assert after[0] > before[0], 'ROUTE_SHAPE_NOT_INSERTED'
    assert after[1] > before[1], 'ROUTE_GEOMETRY_NOT_VISIBLE'

    # Independently check the generated route against the ORIGINAL blocker.
    routed = route_region(result.points, xs.width_um, ly)
    clear, _, _ = check_route_clearance(routed, blocker, ly, rules)
    print('Independent obstacle clearance:', clear)
    assert clear, 'ROUTER_IGNORED_WG_POLYGON_OBSTACLE'
    print('Obstacle-aware placement: PASS; %.3f um (%s)' %
          (result.length_um, result.variant))


def test_rejected_route_does_not_mutate():
    ly = pya.Layout()
    ly.dbu = 0.001
    cell = ly.create_cell('REJECT_TEST')
    wg = ly.layer(pya.LayerInfo(1, 0))
    cell.shapes(wg).insert(pya.DBox(-15, -15, 15, 15).to_itype(ly.dbu))
    xs = WaveguideCrossSection('strip', 0.5, 5.0)
    rules = DesignRules(0.4, 0.5, 5.0)
    before = snapshot(cell, wg)
    rejected = route_between_ports_v64(
        cell, ly, Port(0, 0, (1, 0)), Port(80, 0, (-1, 0)), xs, rules)
    after = snapshot(cell, wg)
    report('Rejected route', ly, cell, wg, before, after, rejected)
    assert not rejected.valid, 'UNSAFE_ROUTE_ACCEPTED'
    assert after[:2] == before[:2], 'REJECTED_ROUTE_MUTATED_LAYOUT'
    print('Rejected route does not modify layout: PASS')


def main():
    test_obstacle_avoidance()
    test_rejected_route_does_not_mutate()
    print('Phase 3E-6 KLayout smoke: PASS')


if __name__ == '__main__':
    main()
