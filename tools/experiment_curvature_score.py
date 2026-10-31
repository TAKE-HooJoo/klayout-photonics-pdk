"""Phase 3E-7.8D-3: exploratory score sweep from v6.5 benchmark CSV.

No router modifications. Candidate rows are observed mode outputs, not the
complete internal AUTO_QUALITY candidate pool. Geometric metrics are sampled.
"""
import argparse
import csv
import math
from pathlib import Path

DEFAULT_INPUT = Path('tests/phase3e78d1_output/route_quality_benchmark.csv')
DEFAULT_OUTPUT = Path('tests/phase3e78d3_output')
WEIGHTS = [(1.0, 1.0, j) for j in (0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0)]
FIELDS = ('length_um', 'curvature_energy_inv_um', 'max_delta_curvature_inv_um')


def read_cases(path):
    cases = {}
    with path.open(newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            if row['valid'].strip().lower() != 'true':
                continue
            for field in FIELDS:
                row[field] = float(row[field])
                if not math.isfinite(row[field]) or row[field] < 0:
                    raise ValueError('invalid metric: ' + field)
            cases.setdefault(row['case'], []).append(row)
    return cases


def score_case(rows, weights):
    """Normalize L by minimum; E and J by maximum, within one case."""
    refs = (min(r[FIELDS[0]] for r in rows),
            max(r[FIELDS[1]] for r in rows),
            max(r[FIELDS[2]] for r in rows))
    if refs[0] <= 0:
        raise ValueError('non-positive route length')
    result = []
    for row in rows:
        terms = [row[FIELDS[i]] / refs[i] if refs[i] > 0 else 0.0
                 for i in range(3)]
        total = sum(w*t for w, t in zip(weights, terms))
        result.append((row, terms, total))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    cases = read_cases(args.input)
    if not cases:
        raise ValueError('no valid routes')
    args.output.mkdir(parents=True, exist_ok=True)
    detail = []
    winners = []
    for case, rows in cases.items():
        # AUTO and EULER can share the same geometry; avoid counting duplicates
        # as independent choices, but preserve all mode labels in detail.
        for weights in WEIGHTS:
            evaluated = score_case(rows, weights)
            for row, terms, total in evaluated:
                detail.append(dict(case=case, mode=row['mode'], variant=row['variant'],
                                   w_length=weights[0], w_energy=weights[1], w_jump=weights[2],
                                   normalized_length=terms[0], normalized_energy=terms[1],
                                   normalized_jump=terms[2], score=total))
            winner = min(evaluated, key=lambda x: (x[2], x[0]['length_um'], x[0]['variant']))
            winners.append(dict(case=case, w_length=weights[0], w_energy=weights[1],
                                w_jump=weights[2], selected_mode=winner[0]['mode'],
                                selected_variant=winner[0]['variant'], score=winner[2]))
            print('%-17s wJ=%-4g -> %-13s %-13s score=%.6f' %
                  (case, weights[2], winner[0]['mode'], winner[0]['variant'], winner[2]))
    for name, data in [('score_sweep.csv', detail), ('score_winners.csv', winners)]:
        with (args.output / name).open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    print('Phase 3E-7.8D-3 score experiment: PASS')


if __name__ == '__main__':
    main()
