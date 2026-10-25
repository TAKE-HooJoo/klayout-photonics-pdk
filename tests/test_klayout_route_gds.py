"""Run: klayout -b -r tests/test_klayout_route_gds.py"""
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pya
from photonics.circuit.geometry import Point
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.obstacle_router_v2 import route_with_waypoints
from photonics.integration.route_gds_klayout import export_route_gds
from photonics.integration.clearance_klayout import waveguide_region, check_route_clearance


def main():
    layout = pya.Layout()
    layout.dbu = 0.001
    xs = WaveguideCrossSection('strip', 0.5, 5.0)
    rules = DesignRules(0.4, 0.5, 5.0)
    blocker = pya.Region(pya.DBox(37, -3, 43, 3).to_itype(layout.dbu))
    result = route_with_waypoints(Point(0, 0), Point(80, 0),
                                  (1, 0), (-1, 0), xs, rules, layout, blocker)
    assert result.valid and result.variant == 'WAYPOINT_CSC', result
    print('Waypoint detour: PASS')

    output_dir = os.path.join(ROOT, 'tests', 'phase3e5_output')
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    output = os.path.join(output_dir, 'waypoint_detour.gds')
    metadata = export_route_gds(result, xs, rules, blocker, output,
                                dbu=layout.dbu)
    assert os.path.isfile(output) and os.path.getsize(output) > 0
    assert metadata['clearance_pass']
    print('GDS export: PASS')

    reopened = pya.Layout()
    reopened.read(output)
    top = reopened.cell('PHOTONICS_ROUTE_TEG')
    assert top is not None
    wg = waveguide_region(top, reopened)
    assert not wg.is_empty()
    obs_layer = reopened.find_layer(pya.LayerInfo(90, 0))
    assert obs_layer is not None and obs_layer >= 0
    obstacles = pya.Region(top.begin_shapes_rec(obs_layer)).merged()
    assert not obstacles.is_empty()
    port_layer = reopened.find_layer(pya.LayerInfo(2, 0))
    assert port_layer is not None and port_layer >= 0
    ports = pya.Region(top.begin_shapes_rec(port_layer))
    assert not ports.is_empty()
    passes, _, _ = check_route_clearance(wg, obstacles, reopened, rules)
    assert passes, 'Clearance failed after GDS round-trip'
    print('GDS round-trip and clearance: PASS')
    print('Variant: %s; Length: %.3f um' % (result.variant, result.length_um))
    print('GDS: %s' % output)
    print('Phase 3E-5 KLayout integration: PASS')


if __name__ == '__main__':
    main()
