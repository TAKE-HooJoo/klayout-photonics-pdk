"""Phase 3E-6.1: dedicated 90/0 obstacle must affect GUI adapter routing.
Run: klayout -b -r tests/test_router_v64_obstacle_layer.py
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
from photonics.integration.obstacle_router import route_region
from photonics.integration.clearance_klayout import check_route_clearance

class Port:
    width = 0.5
    def __init__(self, x, y, direction):
        self.position = pya.DPoint(x, y)
        self.direction = direction

def run():
    ly = pya.Layout()
    ly.dbu = 0.001
    cell = ly.create_cell('OBSTACLE_LAYER_90_TEST')
    wg = ly.layer(pya.LayerInfo(1, 0))
    keepout = ly.layer(pya.LayerInfo(90, 0))
    blocker = pya.Region(pya.DBox(37, -3, 43, 3).to_itype(ly.dbu))
    cell.shapes(keepout).insert(blocker)
    xs = WaveguideCrossSection('strip', 0.5, 5.0)
    rules = DesignRules(0.4, 0.5, 5.0)
    count_before = cell.shapes(wg).size()
    result = route_between_ports_v64(cell, ly, Port(0, 0, (1, 0)),
                                     Port(80, 0, (-1, 0)), xs, rules,
                                     obstacle_layer=pya.LayerInfo(90, 0))
    print('Route valid:', result.valid)
    print('Route variant:', result.variant)
    print('Route reason:', result.reason)
    print('WG shapes before/after:', count_before, cell.shapes(wg).size())
    assert result.valid, result.reason
    assert result.variant == 'WAYPOINT_CSC', result.variant
    routed = route_region(result.points, xs.width_um, ly)
    clear, _, _ = check_route_clearance(routed, blocker, ly, rules)
    print('Independent 90/0 clearance:', clear)
    assert clear, 'KEEP_OUT_90_IGNORED'
    assert cell.shapes(wg).size() > count_before, 'ROUTE_NOT_INSERTED'
    assert cell.shapes(keepout).size() == 1, 'KEEP_OUT_LAYER_MUTATED'
    print('Phase 3E-6.1 obstacle layer: PASS')

if __name__ == '__main__':
    run()
