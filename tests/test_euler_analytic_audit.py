#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_euler_analytic import evaluate_case

for offset in (15., -15., 5.):
    d = evaluate_case((0., 0.), (80., offset), 0., 6.25, 201)
    assert d['valid'], d
    assert d['join_count'] == 3
    assert d['max_heading_jump_deg'] < 1e-9
    assert d['max_curvature_jump_inv_um'] < 1e-9
    assert abs(d['analytic_peak_curvature_inv_um'] - .16) < 1e-12
    assert d['endpoint_error_um'] <= .01
print('Phase 3E-7.8D-10 source-aware tests: PASS')
