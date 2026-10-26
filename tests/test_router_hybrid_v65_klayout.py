"""Run: klayout -b -r tests/test_router_hybrid_v65_klayout.py"""
import os
import sys
sys.path.insert(0, os.getcwd())
import pya
from dataclasses import dataclass
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.router_hybrid_v65 import route_between_ports_hybrid

@dataclass
class Port:
    position: object
    direction: tuple
    width: float = 0.5


def make_layout(block=False):
    ly = pya.Layout()
    ly.dbu = 0.001
    cell = ly.create_cell('HYBRID_TEST')
    if block:
        li = ly.layer(pya.LayerInfo(90, 0))
        # Encloses the source port: no legal exit, keepout is NOT clipped.
        cell.shapes(li).insert(pya.DBox(-3, -3, 3, 3).to_itype(ly.dbu))
    return ly, cell

xs = WaveguideCrossSection('strip', 0.5, 6.25)
rules = DesignRules(0.4, 0.5, 6.25)
source = Port(pya.DPoint(0, 0), (1.0, 0.0))
# Destination OUTWARD points down; arrival is upward.
destination = Port(pya.DPoint(40, 40), (0.0, -1.0))
outdir = os.path.join(os.getcwd(), 'tests', 'phase3e76d_output')
os.makedirs(outdir, exist_ok=True)

for mode, expected in [('EULER', 'EULER'), ('AUTO', 'EULER'), ('CSC', None)]:
    ly, cell = make_layout()
    result = route_between_ports_hybrid(cell, ly, source, destination, xs, rules, mode=mode)
    print('%s: valid=%s variant=%s reason=%s length=%.6f' %
          (mode, result.valid, result.variant, result.reason, result.length_um))
    assert result.valid, '%s failed: %s' % (mode, result.reason)
    if expected:
        assert result.variant == expected
    path = os.path.join(outdir, 'hybrid_%s.gds' % mode.lower())
    ly.write(path)
    print('GDS:', path)

ly, cell = make_layout(block=True)
wg_index = ly.layer(pya.LayerInfo(1, 0))
before = cell.shapes(wg_index).size()
result = route_between_ports_hybrid(cell, ly, source, destination, xs, rules, mode='AUTO')
after = cell.shapes(wg_index).size()
print('Blocked AUTO: valid=%s reason=%s shapes=%d -> %d' %
      (result.valid, result.reason, before, after))
assert not result.valid
assert before == after, 'Invalid route mutated waveguide shapes'
print('Phase 3E-7.6D hybrid KLayout integration: PASS')
