import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

"""Phase 3E-7.8C-2: run with klayout -b -r tests/test_router_quality_v65.py"""
from dataclasses import dataclass
import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.router_hybrid_v65 import route_between_ports_hybrid

@dataclass
class Port:
    position: object
    direction: tuple
    width: float = 0.5

xs = WaveguideCrossSection('strip', 0.5, 6.25)
rules = DesignRules(0.4, 0.5, 6.25)
source = Port(pya.DPoint(0, 0), (1.0, 0.0))
destination = Port(pya.DPoint(80, 15), (-1.0, 0.0))

for mode in ('AUTO', 'CSC', 'EULER', 'AUTO_QUALITY'):
    layout = pya.Layout()
    layout.dbu = 0.001
    cell = layout.create_cell('TOP')
    layer = layout.layer(pya.LayerInfo(1, 0))
    before = cell.shapes(layer).size()
    result = route_between_ports_hybrid(cell, layout, source, destination, xs, rules, mode=mode)
    after = cell.shapes(layer).size()
    print('%s: valid=%s variant=%s reason=%s length=%.6f shapes=%d->%d' %
          (mode, result.valid, result.variant, result.reason, result.length_um, before, after))
    assert result.valid and after == before + 1, 'failed: ' + mode

# A keepout covering the source must reject all candidates without insertion.
layout = pya.Layout()
layout.dbu = 0.001
cell = layout.create_cell('BLOCKED')
wg = layout.layer(pya.LayerInfo(1, 0))
ko = layout.layer(pya.LayerInfo(90, 0))
cell.shapes(ko).insert(pya.DBox(-3, -3, 3, 3).to_itype(layout.dbu))
result = route_between_ports_hybrid(cell, layout, source, destination, xs, rules, mode='AUTO_QUALITY')
print('BLOCKED: valid=%s reason=%s shapes=%d' % (result.valid, result.reason, cell.shapes(wg).size()))
assert not result.valid and cell.shapes(wg).size() == 0
print('Phase 3E-7.8C-2 AUTO_QUALITY: PASS')
