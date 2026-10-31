# Phase 3E-7.8D-16: fixed-physical-span curvature diagnostics

## Scope

An independent numerical diagnostic, not a production router or scoring change. Captures candidates passed to `evaluate_route_quality` during live `AUTO_QUALITY` and compares original Phase 14 metrics with an alternate fixed-physical-span evaluator. It preserves the original production evaluator return value and restores the function in `finally`.

## Install

From repository root, unzip this archive preserving directories. Requires existing Phase 14 `tools/live_shadow_quality_v2.py` and KLayout Python environment.

```bash
python3 tests/test_phase3e78d16.py
klayout -b -r tests/run_phase3e78d16_klayout.py
cat tests/phase3e78d16_output/convergence_summary.csv
cat tests/phase3e78d16_output/mirror_symmetry.csv
```

## Outputs

- `fixed_span_ds_sweep.csv`: original and alternate metrics per live accepted candidate and ds.
- `convergence_summary.csv`: range of values over ds sweep, not an analytic convergence proof.
- `mirror_symmetry.csv`: symmetry check for Euler and CSC mirrored cases.

## Interpretation and limitations

The alternate estimator computes symmetric tangent secants over a **fixed 1 µm physical distance**, then curvature as heading difference over another fixed 1 µm. Its gradient is a fixed-1 µm finite difference of the estimated curvature. It excludes boundary samples where full spans cannot be formed. Thus its integral is an **interior-only proxy**, not full-route curvature energy; do not compare its absolute values directly to Phase 14 energy or use it as an optical-loss metric.

CSC ideal curvature jump is reported separately as 1/R; Euler analytical jump proxy is 0. The finite-span gradient still reflects smoothed CSC discontinuities; do not add it to a jump penalty without considering double counting. Analytical Euler curvature vs arclength is **not** reconstructed here, since the centerline-only capture does not expose an authoritative analytical parameterization. This phase compares numerical estimators and analytic *junction jump proxies*, not complete analytical curvature curves.

The evaluator wrapper captures candidates passed to the production quality evaluator, not necessarily every geometrically generated candidate. The script assumes Phase 14 behavior that each captured candidate matches one valid explicit CSC/EULER route. Failures are reported rather than silently guessing variants.

Do not interpret these diagnostics as GDS G2 continuity, verified bend radius, or photonic propagation loss. No Production `AUTO_QUALITY` changes are made.
