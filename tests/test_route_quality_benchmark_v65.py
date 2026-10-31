"""Phase 3E-7.8D-1: KLayout batch benchmark (no production router changes).
Run: klayout -b -r tests/test_route_quality_benchmark_v65.py
"""
import os
import sys

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import csv
import os
from dataclasses import dataclass
import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.router_hybrid_v65 import route_between_ports_hybrid
from photonics.routing.route_quality import evaluate_route_quality
from photonics.routing.geometry import tangent_errors

@dataclass
class Port:
    position: object
    direction: tuple
    width: float = 0.5

MODES = ('AUTO', 'CSC', 'EULER', 'AUTO_QUALITY')
CASES = (('baseline_80_15', 80.0, 15.0), ('offset_120_25', 120.0, 25.0))
OUT = os.path.join('tests', 'phase3e78d1_output')
os.makedirs(OUT, exist_ok=True)
xs = WaveguideCrossSection('strip', 0.5, 6.25)
rules = DesignRules(0.4, 0.5, 6.25)
rows = []
for case, dx, dy in CASES:
    source = Port(pya.DPoint(0, 0), (1.0, 0.0))
    destination = Port(pya.DPoint(dx, dy), (-1.0, 0.0))
    for mode in MODES:
        layout = pya.Layout()
        layout.dbu = 0.001
        cell = layout.create_cell('BENCH_' + mode)
        wg = layout.layer(pya.LayerInfo(1, 0))
        result = route_between_ports_hybrid(cell, layout, source, destination,
                                            xs, rules, mode=mode)
        shapes = cell.shapes(wg).size()
        assert shapes == (1 if result.valid else 0), (case, mode, shapes)
        row = dict(case=case, mode=mode, valid=result.valid,
                   variant=result.variant, reason=result.reason or '',
                   length_um='', min_radius_um='', max_curvature_inv_um='',
                   curvature_energy_inv_um='', max_delta_curvature_inv_um='',
                   tangent_start_deg='', tangent_end_deg='', points='',
                   relative_score='')
        if result.valid:
            q = evaluate_route_quality(result.points)
            e0, e1 = tangent_errors(result.points, source.direction, destination.direction)
            row.update(length_um=q.length_um,
                       min_radius_um=q.min_sampled_radius_um,
                       max_curvature_inv_um=q.max_abs_curvature_inv_um,
                       curvature_energy_inv_um=q.curvature_energy_inv_um,
                       max_delta_curvature_inv_um=q.max_sampled_delta_curvature_inv_um,
                       tangent_start_deg=e0,
                       tangent_end_deg=e1,
                       points=q.point_count)
            layout.write(os.path.join(OUT, '%s_%s.gds' % (case, mode.lower())))
        rows.append(row)
        print('%-17s %-12s valid=%s variant=%s length=%s reason=%s' %
              (case, mode, result.valid, result.variant, row['length_um'], row['reason']))
    valid = [r for r in rows if r['case'] == case and r['valid']]
    if valid:
        min_len = min(r['length_um'] for r in valid)
        max_energy = max(r['curvature_energy_inv_um'] for r in valid)
        for r in valid:
            r['relative_score'] = (r['length_um'] / min_len +
                (r['curvature_energy_inv_um'] / max_energy if max_energy else 0))
        # This is a cross-mode diagnostic, NOT necessarily the internal AUTO_QUALITY score:
        # AUTO_QUALITY scores all accepted candidates, some not exposed by mode results.
        assert all(r['relative_score'] >= 1 for r in valid)
assert any(r['valid'] for r in rows), 'No valid benchmark routes'
path = os.path.join(OUT, 'route_quality_benchmark.csv')
with open(path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print('CSV:', os.path.abspath(path))
print('Phase 3E-7.8D-1 benchmark: PASS')
