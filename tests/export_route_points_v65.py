"""Phase 3E-7.8D-4: export routed centerlines, without changing production router."""
import csv
import os
import sys
from dataclasses import dataclass
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.router_hybrid_v65 import route_between_ports_hybrid

@dataclass
class Port:
    position: object
    direction: tuple
    width: float = 0.5

CASES = (('baseline_80_15', 80., 15.), ('offset_120_25', 120., 25.))
MODES = ('AUTO', 'CSC', 'EULER', 'AUTO_QUALITY')
OUT = os.path.join(ROOT, 'tests', 'phase3e78d4_output')
os.makedirs(OUT, exist_ok=True)
xs = WaveguideCrossSection('strip', 0.5, 6.25)
rules = DesignRules(0.4, 0.5, 6.25)
rows = []
for case, dx, dy in CASES:
    src = Port(pya.DPoint(0, 0), (1., 0.))
    dst = Port(pya.DPoint(dx, dy), (-1., 0.))
    for mode in MODES:
        ly = pya.Layout()
        ly.dbu = .001
        cell = ly.create_cell('BENCH_' + mode)
        wg = ly.layer(pya.LayerInfo(1, 0))
        r = route_between_ports_hybrid(cell, ly, src, dst, xs, rules, mode=mode)
        assert cell.shapes(wg).size() == (1 if r.valid else 0)
        print('%s %-12s valid=%s variant=%s reason=%s' % (case, mode, r.valid, r.variant, r.reason or ''))
        if r.valid:
            for i, p in enumerate(r.points):
                rows.append({'case':case, 'mode':mode, 'variant':r.variant,
                             'designed_radius_um':r.designed_radius_um,
                             'index':i, 'x_um':p.x, 'y_um':p.y})
assert rows, 'No valid route points'
path = os.path.join(OUT, 'route_centerlines.csv')
with open(path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print('Centerlines:', path)
print('Phase 3E-7.8D-4 export: PASS')
