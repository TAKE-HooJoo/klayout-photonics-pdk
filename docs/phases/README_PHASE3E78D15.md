# Phase 3E-7.8D-15 — Live Shadow v2 sampling stability

This phase tests numerical sampling sensitivity **without changing** the production router, production quality evaluator, or placement decisions.

## Run

From the repository root, after installing the ZIP over the existing Phase 14 files:

```bash
python3 tests/test_live_shadow_convergence.py
klayout -b -r tests/run_phase3e78d15_klayout.py
cat tests/phase3e78d15_output/convergence_summary.csv
cat tests/phase3e78d15_output/ds_sweep_winners.csv
cat tests/phase3e78d15_output/mirror_symmetry.csv
```

## Method

The KLayout runner temporarily observes the exact accepted centerlines passed to the production `evaluate_route_quality`, retaining its return values and exceptions. It identifies candidates using independent CSC/EULER runs with matching point sequences, then restores the original evaluator. Only one production route is placed per successful test case.

For each captured polyline, `centerline_metrics(points, ds, window=1.0)` is run at `ds = 0.2, 0.1, 0.05, 0.025, 0.0125 µm`. This changes only the numerical resampling interval; the fixed smoothing window and source polyline are held constant. Shadow scores are normalized **within each case and ds**, so raw scores across cases are not directly comparable. Weights are `(1,1,1,1)`.

CSC's jump `1/R` and Euler's zero jump are **ideal analytical proxies**, not observed GDS junction properties. The maximum curvature gradient is a fixed-window numerical proxy and can change with ds, especially around CSC junctions. The convergence summary reports the relative range across tested ds values, **not a proof of analytic convergence**. The runner also compares mirrored baseline/negative routes for each ds.

## Outputs

- `ds_sweep_candidate_scores.csv`: all metrics, normalizations, and scores.
- `ds_sweep_winners.csv`: production reference, shadow winner, score margin, candidate count, shape delta.
- `convergence_summary.csv`: per-variant energy, gradient and score relative ranges; winner stability.
- `mirror_symmetry.csv`: absolute metric differences for LSR/RSL and Euler mirror pairs.
- `production_reference.csv`: production choice and placement audit.

## Boundaries

- No foundry DRC signoff, no optical loss model, no GDS G2 proof.
- The Python monkeypatch observer is diagnostic, not a public candidate API.
- Stability of the winner does not imply metric convergence or physically justified score weights.
- If the production source or accepted candidate set changes, compare against a new baseline.
