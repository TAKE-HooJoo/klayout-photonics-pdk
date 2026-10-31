"""Phase 3E-7.8D-7: audit radius, convergence and experimental scores.

Uses D-6 CSV and D-4 exported centerlines; no router changes.
"""
import argparse
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D6 = ROOT / 'tests/phase3e78d6_output/curvature_gradient_sweep.csv'
OUT = ROOT / 'tests/phase3e78d7_output'


def read_rows(path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def validate_jump(row, tolerance=1e-8):
    radius = float(row['designed_radius_um'])
    declared = row['ideal_csc_line_arc_jump_inv_um']
    if not declared:
        return 'NOT_AVAILABLE', None, None
    value = float(declared)
    expected = 1.0 / radius
    return ('CONSISTENT' if math.isclose(value, expected, abs_tol=tolerance, rel_tol=tolerance)
            else 'MISMATCH'), expected, value


def convergence(rows):
    """Compare the finest two spacings, not a proof of convergence."""
    ordered = sorted(rows, key=lambda r: float(r['actual_step_um']))
    if len(ordered) < 2:
        return None
    a, b = ordered[0], ordered[1]
    g0 = float(a['max_abs_window_gradient_inv_um2'])
    g1 = float(b['max_abs_window_gradient_inv_um2'])
    return {'finest_step_um': float(a['actual_step_um']),
            'next_step_um': float(b['actual_step_um']),
            'finest_gmax_inv_um2': g0,
            'next_gmax_inv_um2': g1,
            'relative_change': abs(g0-g1)/max(abs(g0), abs(g1), 1e-15)}


def experimental_score(length, energy, gradient, jump, references, weights):
    """Only compare routes in one case with identical window/step settings.

    Missing analytic jump is not treated as zero: result unavailable.
    """
    if jump is None:
        return None
    vals = (length, energy, gradient, jump)
    return sum(w*v/ref for w,v,ref in zip(weights, vals, references))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, default=D6)
    p.add_argument('--output', type=Path, default=OUT)
    p.add_argument('--assume-euler-c1', action='store_true',
                   help='Experimental assumption: Euler curvature jump=0; NOT verified by route metadata')
    p.add_argument('--weights', type=float, nargs=4, default=[1, 1, 1, 1],
                   metavar=('WL','WE','WG','WJ'))
    a = p.parse_args()
    if any(w < 0 or not math.isfinite(w) for w in a.weights):
        p.error('weights must be finite and nonnegative')
    if not a.input.exists():
        p.error('missing D-6 CSV; run python3 tools/analyze_curvature_gradient.py first')
    rows = read_rows(a.input)
    if not rows:
        p.error('empty D-6 CSV')
    a.output.mkdir(parents=True, exist_ok=True)
    audit = []
    groups = {}
    for row in rows:
        status, expected, observed = validate_jump(row)
        audit.append(dict(case=row['case'], mode=row['mode'], variant=row['variant'],
                          requested_step_um=row['requested_step_um'],
                          designed_radius_um=row['designed_radius_um'],
                          expected_1_over_radius_inv_um='' if expected is None else expected,
                          reported_jump_inv_um='' if observed is None else observed,
                          consistency=status,
                          source_note='ideal_CSC_topology_not_geometry_verified' if observed is not None else 'unknown_not_zero'))
        groups.setdefault((row['case'], row['mode'], row['variant']), []).append(row)
    for row in audit:
        if row['consistency'] == 'MISMATCH':
            print('WARNING radius/jump mismatch:', row)
    with (a.output/'jump_radius_audit.csv').open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(audit[0])); w.writeheader(); w.writerows(audit)
    summaries=[]
    for key, rr in sorted(groups.items()):
        c=convergence(rr)
        if c is None: continue
        summaries.append(dict(case=key[0],mode=key[1],variant=key[2],**c))
        print('%-17s %-12s %-12s Gmax fine=%9.6f relative change=%7.3f%%' %
              (key[0],key[1],key[2],c['finest_gmax_inv_um2'],100*c['relative_change']))
    if summaries:
        with (a.output/'gradient_convergence.csv').open('w', newline='', encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(summaries[0])); w.writeheader(); w.writerows(summaries)
    # D-6 lacks path length: join D-5 CSV, which records path length and window energy.
    d5 = ROOT/'tests/phase3e78d5_output/curvature_window_sweep.csv'
    if d5.exists():
        energies={(r['case'],r['mode'],r['variant'],r['requested_step_um']):r for r in read_rows(d5)}
        score_rows=[]
        for case in sorted({r['case'] for r in rows}):
            candidates=[]
            for (c,mode,variant),rr in groups.items():
                if c != case: continue
                r=min(rr,key=lambda x:float(x['actual_step_um']))
                e=energies.get((c,mode,variant,r['requested_step_um']))
                if e is None: continue
                status, _, jump = validate_jump(r)
                if jump is None and a.assume_euler_c1 and variant.startswith('EULER'):
                    jump=0.0
                candidates.append((mode,variant,float(e['length_um']),float(e['window_energy_inv_um']),
                                   float(r['max_abs_window_gradient_inv_um2']),jump,status))
            if not candidates: continue
            refs=[max(v[i] for v in candidates) for i in (2,3,4)]
            jump_values=[v[5] for v in candidates if v[5] is not None]
            refs.append(max(jump_values) if jump_values else 0.0)
            refs=[v if v>0 else 1.0 for v in refs]
            for mode,variant,length,energy,gradient,jump,status in candidates:
                score=experimental_score(length,energy,gradient,jump,refs,a.weights)
                score_rows.append(dict(case=case,mode=mode,variant=variant,length_um=length,
                    window_energy_inv_um=energy,window_gradient_inv_um2=gradient,
                    jump_inv_um='' if jump is None else jump,
                    jump_assumption='Euler_C1_UNVERIFIED' if jump==0 and variant.startswith('EULER') else status,
                    experimental_score='' if score is None else score,
                    comparable='YES_ASSUMPTION' if score is not None and a.assume_euler_c1 else 'NO_UNVERIFIED_JUMP'))
        if score_rows:
            with (a.output/'integrated_score_experimental.csv').open('w',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,fieldnames=list(score_rows[0]));w.writeheader();w.writerows(score_rows)
            print('Experimental scores:',a.output/'integrated_score_experimental.csv')
    else:
        print('D-5 CSV missing: skip experimental scores; run D-5 analysis first')
    print('Radius audit:', a.output/'jump_radius_audit.csv')
    print('Gradient convergence:', a.output/'gradient_convergence.csv')
    print('Phase 3E-7.8D-7 diagnostic: PASS (not proof of physical validity)')


if __name__=='__main__':
    main()
