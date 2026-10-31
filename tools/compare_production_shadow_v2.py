#!/usr/bin/env python3
"""Phase 3E-7.8D-13: read actual KLayout production run and offline shadow reference.
No router monkeypatch, no production modifications, no live candidate-score equivalence claim.
"""
import argparse
import csv
from pathlib import Path

DEFAULT_PRODUCTION = Path('tests/phase3e78d13_output/production_routes.csv')
DEFAULT_SHADOW = Path('tests/phase3e78d12_output/shadow_quality_comparison.csv')
DEFAULT_OUTPUT = Path('tests/phase3e78d13_output/production_shadow_comparison.csv')

def read_csv(path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def compare(prod, shadow, weight=1.0):
    refs = {}
    for r in shadow:
        if abs(float(r['weight_jump'])-weight) < 1e-9:
            if r['case'] in refs:
                raise ValueError('duplicate shadow case: '+r['case'])
            refs[r['case']] = r
    out=[]
    for r in prod:
        if r['mode'] != 'AUTO_QUALITY':
            continue
        ref=refs.get(r['case'])
        variant = r['variant'] if r['valid'] == 'True' else ''
        shadow_variant = ref['shadow_winner'] if ref else ''
        out.append(dict(case=r['case'],production_valid=r['valid'],production_variant=variant,
                        production_reason=r['reason'],production_length_um=r['length_um'],
                        production_shape_delta=r['shape_delta'],production_point_count=r['point_count'],
                        shadow_reference_variant=shadow_variant,weight_jump=weight,
                        match=(str(variant==shadow_variant) if ref and variant else 'NOT_COMPARABLE'),
                        scope='PRODUCTION_RUN_VS_HISTORICAL_OFFLINE_SHADOW_NOT_SAME_CANDIDATES'))
    if not out:
        raise ValueError('No production AUTO_QUALITY rows')
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--production',type=Path,default=DEFAULT_PRODUCTION)
    ap.add_argument('--shadow',type=Path,default=DEFAULT_SHADOW)
    ap.add_argument('--output',type=Path,default=DEFAULT_OUTPUT)
    ap.add_argument('--weight-jump',type=float,default=1.)
    args=ap.parse_args()
    if not args.production.exists():
        ap.error('Run klayout -b -r tests/run_phase3e78d13_klayout.py first')
    if not args.shadow.exists():
        ap.error('Run python3 tools/shadow_quality_v2.py first')
    rows=compare(read_csv(args.production),read_csv(args.shadow),args.weight_jump)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    for r in rows:
        print('{case}: production={production_variant} shadow_reference={shadow_reference_variant} match={match}'.format(**r))
    print('Phase 3E-7.8D-13: comparison complete (historical offline reference, NOT live shadow scoring)')

if __name__=='__main__': main()
