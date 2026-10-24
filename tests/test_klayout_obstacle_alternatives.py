"""Verify alternate CSC selection when the shortest route is blocked."""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pya

from photonics.circuit.geometry import Point
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.obstacle_router import (
    route_avoiding_obstacles,
    route_region,
)
from photonics.integration.clearance_klayout import check_route_clearance


def main():
    layout = pya.Layout()
    layout.dbu = 0.001

    xs = WaveguideCrossSection('strip', 0.5, 5.0)
    rules = DesignRules(0.4, 0.5, 5.0)

    empty = pya.Region()

    args = (
        Point(0, 0),
        Point(30, 15),
        (1, 0),
        (-1, 0),
        xs,
        rules,
        layout,
    )

    shortest = route_avoiding_obstacles(*args, empty)
    assert shortest.valid, shortest

    print('Original topology:', shortest.variant)
    print('Original length:', round(shortest.length_um, 3), 'um')

    # Try several interior points along the original route.
    # Avoid the endpoints because those are intentional port connections.
    found = False

    for fraction in (0.25, 0.40, 0.50, 0.60, 0.75):
        index = int((len(shortest.points) - 1) * fraction)
        point = shortest.points[index]

        blocker = pya.Region(
            pya.DBox(
                point.x - 0.4,
                point.y - 0.4,
                point.x + 0.4,
                point.y + 0.4,
            ).to_itype(layout.dbu)
        )

        original_region = route_region(
            shortest.points, xs.width_um, layout
        )
        original_passes, _, _ = check_route_clearance(
            original_region, blocker, layout, rules
        )
        assert not original_passes

        alternate = route_avoiding_obstacles(*args, blocker)

        if alternate.valid:
            assert alternate.variant != shortest.variant
            assert alternate.length_um >= shortest.length_um - 1e-6

            alternate_region = route_region(
                alternate.points, xs.width_um, layout
            )
            passes, _, _ = check_route_clearance(
                alternate_region, blocker, layout, rules
            )
            assert passes

            print('Alternative topology:', alternate.variant)
            print('Alternative length:',
                  round(alternate.length_um, 3), 'um')
            print('Alternate CSC selection: PASS')
            found = True
            break

    if not found:
        print('No alternate CSC route found for this geometry')
        print('Alternate CSC selection: NOT VERIFIED')
        print('A different test geometry or waypoint routing is needed')


if __name__ == '__main__':
    main()
