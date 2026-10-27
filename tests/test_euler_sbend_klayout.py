"""Run: klayout -b -r tests/test_euler_sbend_klayout.py"""
import os
import sys
import pya

sys.path.insert(0, os.getcwd())
from photonics.integration.router_euler_sbend import route_euler_sbend_klayout

OUT = 'tests/phase3e77b_output'
os.makedirs(OUT, exist_ok=True)


def make_case(name, dst, blocked=False, keepout=False):
    layout = pya.Layout()
    layout.dbu = 0.001
    cell = layout.create_cell(name)
    wg = layout.layer(1, 0)
    ko = layout.layer(90, 0)
    if keepout:
        cell.shapes(ko).insert(pya.Box(35000, 1000, 45000, 20000))
    obstacle = None
    if blocked:
        obstacle = pya.Region(pya.Box(35000, -25000, 45000, 25000))
    before = cell.shapes(wg).size()
    r = route_euler_sbend_klayout(cell, layout, (0, 0), dst, 0, 0,
                                  obstacle_region=obstacle,
                                  obstacle_layer=(90, 0),
                                  clearance_um=0.5)
    after = cell.shapes(wg).size()
    if blocked or keepout:
        assert not r.valid, (name, r)
        assert r.reason == 'OBSTACLE_CLEARANCE_VIOLATION', (name, r.reason)
        assert before == after, (name, 'GDS mutated on failure')
    else:
        assert r.valid, (name, r.reason)
        assert after == before + 1, (name, 'GDS not inserted')
        assert r.endpoint_error_um <= 0.01, (name, r.endpoint_error_um)
        assert r.tangent_error_source_deg <= 5.0, (name, r.tangent_error_source_deg)
        assert r.tangent_error_destination_deg <= 5.0, (name, r.tangent_error_destination_deg)
    layout.write(os.path.join(OUT, name+'.gds'))
    print('%s: valid=%s reason=%s length=%.6f radius=%.6f shapes=%d->%d' %
          (name, r.valid, r.reason, r.length_um, r.sampled_radius_um, before, after))


make_case('euler_sbend_up', (80, 15))
make_case('euler_sbend_down', (80, -15))
make_case('euler_sbend_straight', (80, 0))
make_case('euler_sbend_blocked', (80, 15), blocked=True)
make_case('euler_sbend_keepout', (80, 15), keepout=True)
print('Phase 3E-7.7B KLayout integration: PASS')
