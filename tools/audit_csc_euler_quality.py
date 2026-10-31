#!/usr/bin/env python3
"""Phase 3E-7.8D-11: ideal CSC junction audit and experimental score sweep.

Reads existing Phase 7.8D-7 CSV; does not alter production routing.
"""
import argparse
import csv
import math
from pathlib import Path

DEFAULT_INPUT = Path('tests/phase3e78d7_output/integrated_score_experimental.csv')
DEFAULT_RADIUS = Path('tests/phase3e78d7_output/jump_radius_audit.csv')
DEFAULT_OUTPUT = Path('tests/phase3e78d11_output')


def ideal_csc_junctions(radius_um, topology='LSR'):
    """Ideal CSC piecewise-curvature junctions; G1 is by CSC construction.

    This is a theoretical model, NOT verification of the generated centerline.
    """
    if not math.isfinite(radius_um) or radius_um <= 0:
        raise ValueError('radius must be finite and positive')
    if topology not in ('LSL', 'LSR', 'RSL', 'RSR'):
        raise ValueError('unsupported CSC topology')
    signs = {'L': 1, 'R': -1}
    first, last = signs[topology[0]], signs[topology[2]]
    k = 1.0 / radius_um
    return [
        {'junction': 'arc_to_straight', 'heading_jump_deg': 0.0,
         'curvature_left_inv_um': first*k, 'curvature_right_inv_um': 0.0,
         'abs_jump_inv_um': k},
        {'junction': 'straight_to_arc', 'heading_jump_deg': 0.0,
         'curvature_left_inv_um': 0.0, 'curvature_right_inv_um': last*k,
         'abs_jump_inv_um': k},
    ]


def normalized_scores(rows, weights):
    """Normalize within a single case; smaller scores preferred.

    Normalizers: minimum length; maximum of each other metric. All nonnegative.
    """
    if not rows:
        return []
    fields = ('length_um', 'window_energy_inv_um', 'window_gradient_inv_um2', 'jump_inv_um')
    if len(weights) != 4 or any(not math.isfinite(w) or w < 0 for w in weights):
        raise ValueError('weights must be four nonnegative finite numbers')
    vals = [[float(r[f]) for f in fields] for r in rows]
    if any(any(not math.isfinite(x) or x < 0 for x in v) for v in vals):
        raise ValueError('invalid metric')
    lref = min(v[0] for v in vals)
    if lref <= 0:
        raise ValueError('length must be positive')
    refs = [lref] + [max(v[i] for v in vals) for i in range(1, 4)]
    out = []
    for r, v in zip(rows, vals):
        terms = [v[0]/refs[0]] + [v[i]/refs[i] if refs[i] > 0 else 0.0 for i in range(1, 4)]
        score = sum(w*t for w, t in zip(weights, terms))
        out.append((r, score, terms))
    return out


def load_csv(path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    p.add_argument('--radius-audit', type=Path, default=DEFAULT_RADIUS)
    p.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT)
    p.add_argument('--jump-weights', type=float, nargs='+', default=[0, 0.1, 0.25, 0.5, 1, 2, 5])
    args = p.parse_args()
    if any(not math.isfinite(x) or x < 0 for x in args.jump_weights):
        p.error('jump weights must be nonnegative and finite')
    if not args.input.exists() or not args.radius_audit.exists():
        p.error('Phase 7.8D-7 CSV files not found; run that phase first')
    data = load_csv(args.input)
    radii = load_csv(args.radius_audit)
    radius_map = {}
    for r in radii:
        if r['variant'] in ('LSL', 'LSR', 'RSL', 'RSR') and r['consistency'] == 'CONSISTENT':
            key = (r['case'], r['mode'], r['variant'])
            radius = float(r['designed_radius_um'])
            if key in radius_map and not math.isclose(radius_map[key], radius, rel_tol=1e-10):
                raise ValueError('inconsistent radius audit for ' + str(key))
            radius_map[key] = radius
    junction_rows = []
    unique = set()
    for r in data:
        key = (r['case'], r['mode'], r['variant'])
        if key in unique:
            raise ValueError('duplicate candidate: ' + str(key))
        unique.add(key)
        if r['variant'] in ('LSL', 'LSR', 'RSL', 'RSR'):
            if key not in radius_map:
                raise ValueError('no consistent CSC radius audit for ' + str(key))
            js = ideal_csc_junctions(radius_map[key], r['variant'])
            for j in js:
                junction_rows.append({'case': r['case'], 'mode': r['mode'], 'variant': r['variant'],
                                      'radius_um': radius_map[key], 'scope': 'IDEAL_CSC_MODEL_ONLY', **j})
            expected = max(j['abs_jump_inv_um'] for j in js)
            if not math.isclose(float(r['jump_inv_um']), expected, abs_tol=1e-9):
                raise ValueError('jump mismatch for ' + str(key))
        elif r['variant'] == 'EULER_SBEND':
            if r['jump_assumption'] != 'Euler_C1_UNVERIFIED':
                raise ValueError('unexpected Euler jump provenance: ' + r['jump_assumption'])
            if abs(float(r['jump_inv_um'])) > 1e-12:
                raise ValueError('Euler model expected zero jump')
        else:
            raise ValueError('unknown variant ' + r['variant'])
    write_csv(args.output_dir/'ideal_csc_junctions.csv',
              ['case', 'mode', 'variant', 'radius_um', 'scope', 'junction', 'heading_jump_deg',
               'curvature_left_inv_um', 'curvature_right_inv_um', 'abs_jump_inv_um'], junction_rows)
    # Avoid treating AUTO, EULER, CSC, AUTO_QUALITY duplicates as independent candidates.
    cases = sorted(set(r['case'] for r in data))
    sweep = []
    for case in cases:
        unique_variants = {}
        for r in data:
            if r['case'] == case:
                if r['variant'] in unique_variants:
                    prev = unique_variants[r['variant']]
                    for field in ('length_um', 'window_energy_inv_um', 'window_gradient_inv_um2', 'jump_inv_um'):
                        if not math.isclose(float(r[field]), float(prev[field]), rel_tol=1e-9, abs_tol=1e-12):
                            raise ValueError('different metrics for duplicate variant in ' + case)
                else:
                    unique_variants[r['variant']] = r
        variants = list(unique_variants.values())
        for wj in args.jump_weights:
            scored = normalized_scores(variants, (1, 1, 1, wj))
            winner = min(scored, key=lambda x: (x[1], float(x[0]['length_um']), x[0]['variant']))[0]['variant']
            for r, score, terms in scored:
                sweep.append({'case': case, 'variant': r['variant'], 'weight_length': 1,
                              'weight_energy': 1, 'weight_gradient': 1, 'weight_jump': wj,
                              'normalized_length': terms[0], 'normalized_energy': terms[1],
                              'normalized_gradient': terms[2], 'normalized_jump': terms[3],
                              'experimental_score': score, 'winner': winner,
                              'scope': 'EXPERIMENTAL_GEOMETRIC_NOT_OPTICAL_LOSS'})
        print(case, 'candidates:', ', '.join(sorted(unique_variants)))
        for wj in args.jump_weights:
            winner = next(r['winner'] for r in sweep if r['case'] == case and r['weight_jump'] == wj)
            print('  wJ=%g winner=%s' % (wj, winner))
    write_csv(args.output_dir/'quality_weight_sweep.csv',
              ['case', 'variant', 'weight_length', 'weight_energy', 'weight_gradient', 'weight_jump',
               'normalized_length', 'normalized_energy', 'normalized_gradient', 'normalized_jump',
               'experimental_score', 'winner', 'scope'], sweep)
    print('Phase 3E-7.8D-11: diagnostic complete (ideal CSC only; not GDS verification)')


if __name__ == '__main__':
    main()
