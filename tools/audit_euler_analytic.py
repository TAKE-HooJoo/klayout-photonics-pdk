#!/usr/bin/env python3
"""Phase 3E-7.8D-10: source-aware Euler S-bend analytic join audit."""
import argparse
import csv
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from photonics.routing.euler_bend import symmetric_euler_bend
from photonics.routing.euler_sbend import route_euler_sbend


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


def evaluate_case(source, destination, heading_deg, radius, samples):
    r = route_euler_sbend(source, destination, heading_deg, heading_deg,
                          min_radius_um=radius, samples_per_bend=samples)
    if not r.valid:
        return {'valid': False, 'reason': r.reason}
    if r.bend_angle_deg == 0:
        return {'valid': True, 'reason': 'STRAIGHT_ONLY', 'join_count': 0,
                'max_heading_jump_deg': 0., 'max_curvature_jump_inv_um': 0.,
                'analytic_peak_curvature_inv_um': 0., 'analytic_min_radius_um': math.inf,
                'max_vertex_turn_deg': 0., 'endpoint_error_um': r.endpoint_error_um}
    a = math.radians(r.bend_angle_deg)
    bend = symmetric_euler_bend(r.bend_angle_deg, radius, samples=samples)
    # Join states in the local coordinate system; mirror and rotation reverse curvature.
    # For negative lateral offsets, all signed curvature values flip, but jumps stay zero.
    joins = [
        ('lead_to_bend1', 0., 0., 0., bend[0].curvature),
        ('bend1_to_bend2', a, a, bend[-1].curvature, -bend[0].curvature),
        ('bend2_to_lead', 0., 0., -bend[-1].curvature, 0.),
    ]
    hj = max(abs(math.degrees(wrap(left-right))) for _, left, right, _, _ in joins)
    kj = max(abs(left-right) for _, _, _, left, right in joins)
    # Sampled polygon turn is not a proof of continuous G1/G2.
    max_turn = 0.
    for p0, p1, p2 in zip(r.points, r.points[1:], r.points[2:]):
        u = (p1[0]-p0[0], p1[1]-p0[1])
        v = (p2[0]-p1[0], p2[1]-p1[1])
        if math.hypot(*u) > 1e-12 and math.hypot(*v) > 1e-12:
            max_turn = max(max_turn, abs(math.degrees(math.atan2(u[0]*v[1]-u[1]*v[0], u[0]*v[0]+u[1]*v[1]))))
    return {'valid': True, 'reason': 'ANALYTIC_MODEL_ONLY', 'join_count': len(joins),
            'max_heading_jump_deg': hj, 'max_curvature_jump_inv_um': kj,
            'analytic_peak_curvature_inv_um': 1/radius,
            'analytic_min_radius_um': radius,
            'max_vertex_turn_deg': max_turn, 'endpoint_error_um': r.endpoint_error_um}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default='tests/phase3e78d10_output/euler_analytic_audit.csv')
    ap.add_argument('--samples', type=int, default=201)
    ap.add_argument('--radius', type=float, default=6.25)
    args = ap.parse_args()
    cases = [('baseline_80_15', (0., 0.), (80., 15.)),
             ('offset_120_25', (0., 0.), (120., 25.)),
             ('negative_80_-15', (0., 0.), (80., -15.))]
    records = []
    for name, a, b in cases:
        result = evaluate_case(a, b, 0., args.radius, args.samples)
        records.append({'case': name, **result})
        print(name, result)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    keys = ['case', 'valid', 'reason', 'join_count', 'max_heading_jump_deg',
            'max_curvature_jump_inv_um', 'analytic_peak_curvature_inv_um',
            'analytic_min_radius_um', 'max_vertex_turn_deg', 'endpoint_error_um']
    with out.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(records)
    print('CSV:', out)
    print('Phase 3E-7.8D-10: analytic model audit complete (not polygonal G2 proof)')

if __name__ == '__main__':
    main()
