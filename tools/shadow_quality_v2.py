#!/usr/bin/env python3
"""Phase 3E-7.8D-12: offline shadow scoring; never imports or changes router."""
import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

INPUT = Path('tests/phase3e78d11_output/quality_weight_sweep.csv')
OUTPUT = Path('tests/phase3e78d12_output')
REQUIRED = {'case','variant','weight_length','weight_energy','weight_gradient','weight_jump','normalized_length','normalized_energy','normalized_gradient','normalized_jump','experimental_score','winner'}


def read_rows(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError('Missing columns: ' + ', '.join(sorted(missing)))
        rows = list(reader)
    if not rows:
        raise ValueError('Empty input')
    return rows


def evaluate(rows, tol=1e-8):
    grouped = defaultdict(list)
    for r in rows:
        nums = {k: float(r[k]) for k in ('weight_length','weight_energy','weight_gradient','weight_jump','normalized_length','normalized_energy','normalized_gradient','normalized_jump','experimental_score')}
        if not all(math.isfinite(v) and v >= 0 for v in nums.values()):
            raise ValueError('Nonfinite/negative value')
        computed = sum(nums['weight_'+k]*nums['normalized_'+k] for k in ('length','energy','gradient','jump'))
        if not math.isclose(computed, nums['experimental_score'], rel_tol=tol, abs_tol=tol):
            raise ValueError('Score mismatch: %s/%s wJ=%s' % (r['case'],r['variant'],r['weight_jump']))
        key = (r['case'], nums['weight_length'], nums['weight_energy'], nums['weight_gradient'], nums['weight_jump'])
        grouped[key].append((r['variant'], computed, r['winner']))
    result = []
    for key, options in sorted(grouped.items()):
        # Stable tie break, never assume first row wins.
        winner, best, _ = min(options, key=lambda x: (x[1], x[0]))
        reported = {o[2] for o in options}
        if len(reported) != 1 or winner not in reported:
            raise ValueError('Winner mismatch for %r: calculated=%s reported=%r' % (key,winner,reported))
        runner = sorted(options, key=lambda x:(x[1],x[0]))
        margin = runner[1][1]-best if len(runner)>1 else None
        result.append(dict(case=key[0], weight_length=key[1], weight_energy=key[2],weight_gradient=key[3],weight_jump=key[4],candidate_count=len(options),shadow_winner=winner,previous_winner=next(iter(reported)),score=best,margin_to_second=margin,comparison_scope='OFFLINE_SHADOW_NOT_PRODUCTION'))
    return result


def crossover(rows, case='baseline_80_15'):
    # Determine linear crossing from normalized terms, not hardcoded values.
    by_variant = {}
    for r in rows:
        if r['case'] != case or float(r['weight_jump']) != 0:
            continue
        by_variant[r['variant']] = r
    if 'EULER_SBEND' not in by_variant or 'LSR' not in by_variant:
        return None
    e, c = by_variant['EULER_SBEND'], by_variant['LSR']
    base = lambda r: sum(float(r['weight_'+k])*float(r['normalized_'+k]) for k in ('length','energy','gradient'))
    dj = float(c['normalized_jump'])-float(e['normalized_jump'])
    if abs(dj)<1e-12:
        return None
    return (base(e)-base(c))/dj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,default=INPUT)
    ap.add_argument('--output-dir',type=Path,default=OUTPUT)
    args=ap.parse_args()
    rows=read_rows(args.input)
    results=evaluate(rows)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    out=args.output_dir/'shadow_quality_comparison.csv'
    with out.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0]))
        writer.writeheader();writer.writerows(results)
    threshold=crossover(rows)
    with (args.output_dir/'crossover_summary.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['case','crossover_weight_jump','scope']);writer.writerow(['baseline_80_15', '' if threshold is None else '%.12f'%threshold,'OFFLINE_NORMALIZED_CANDIDATE_SET'])
    for r in results:
        print('%-17s wJ=%-5g shadow=%-12s prior=%s'%(r['case'],r['weight_jump'],r['shadow_winner'],r['previous_winner']))
    print('Crossover wJ:',threshold)
    print('Phase 3E-7.8D-12: PASS (offline shadow parity only)')

if __name__=='__main__':main()
