"""Run: klayout -b -r tests/test_klayout_clearance.py"""
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pya
from photonics.pdk.design_rules import DesignRules
from photonics.integration.clearance_klayout import (
    waveguide_region, check_route_clearance)


def rectangle(x1, y1, x2, y2, dbu):
    return pya.Region(pya.DBox(x1, y1, x2, y2).to_itype(dbu))


def main():
    layout = pya.Layout()
    layout.dbu = 0.001
    rules = DesignRules(0.4, 0.5, 5.0)
    route = rectangle(0, -0.25, 10, 0.25, layout.dbu)

    clear = rectangle(0, 1.05, 10, 1.55, layout.dbu)
    passed, overlap, violation = check_route_clearance(route, clear, layout, rules)
    assert passed and overlap.is_empty() and violation.is_empty(), 'clearance case'
    print('Clearance above minimum: PASS')

    close = rectangle(0, 0.65, 10, 1.15, layout.dbu)
    passed, overlap, violation = check_route_clearance(route, close, layout, rules)
    assert not passed and overlap.is_empty() and not violation.is_empty(), 'spacing case'
    print('Spacing violation: PASS')

    crossing = rectangle(4, -1, 6, 1, layout.dbu)
    passed, overlap, violation = check_route_clearance(route, crossing, layout, rules)
    assert not passed and not overlap.is_empty(), 'crossing case'
    print('Waveguide overlap: PASS')

    wg = layout.layer(pya.LayerInfo(1, 0))
    pin = layout.layer(pya.LayerInfo(2, 0))
    top = layout.create_cell('TOP')
    child = layout.create_cell('CHILD')
    child.shapes(wg).insert(pya.DBox(0, -0.25, 10, 0.25))
    child.shapes(pin).insert(pya.DBox(-1, -1, 11, 1))
    top.insert(pya.DCellInstArray(child.cell_index(), pya.DTrans(pya.DVector(20, 30))))
    hierarchical = waveguide_region(top, layout)
    expected = rectangle(20, 29.75, 30, 30.25, layout.dbu)
    assert (hierarchical ^ expected).is_empty(), 'hierarchy / optical pin filtering'
    print('Hierarchical waveguide Region: PASS')
    print('Phase 3E-2 KLayout integration: PASS')


if __name__ == '__main__':
    main()
