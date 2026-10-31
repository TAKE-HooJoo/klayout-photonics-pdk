# Phase 3E-7.8D-7 — Curvature metric audit and experimental integration

## Purpose

Check the radius behind D-6 `Jr=0.128`, compare Gmax at the two finest available spacings, and prototype a four-term score without changing Router/AUTO_QUALITY.

## Run

```bash
python3 tests/test_curvature_integrated.py
python3 tools/analyze_curvature_integrated.py
# OPTIONAL sensitivity experiment, explicitly assumes Euler curvature continuity:
python3 tools/analyze_curvature_integrated.py --assume-euler-c1 --weights 1 1 1 1
```

Requires previous D-5 and D-6 outputs. Produces `tests/phase3e78d7_output/jump_radius_audit.csv`, `gradient_convergence.csv`, and, if D-5 output exists, `integrated_score_experimental.csv`.

## Interpretation and limitations

- `Jr=0.128 µm^-1` corresponds to `R=7.8125 µm`, **if** D-6 computed `1/R`. This is not the same as a 6.25 µm radius; inspect `designed_radius_um` and Router geometry/metadata to establish the cause. The audit checks only arithmetic consistency, not that a particular arc exists.
- `Gmax` is the gradient of a **fixed-window filtered curvature proxy**, not the analytic continuous curvature gradient. Comparing the finest two sample steps measures stability only; it does not prove convergence.
- Missing Euler jump is **unknown**, not zero. By default the experimental score is left blank for such routes. `--assume-euler-c1` is explicitly an **unverified modeling assumption** for sensitivity analysis.
- The four score terms normalize by the **maximum within each case** for the finest available sample step; lower is preferred only within that case and weight setting. Scores cannot be compared across cases or weight settings. These are not optical loss estimates.
- CSC fixed-window Gmax includes the filtered effect of jumps; counting both Gmax and Jr can double-penalize discontinuities. A future topology-aware segmentation should address this before Router integration.
- AUTO and EULER may duplicate a geometry; the experiment lists both but should not treat them as independent physical routes.

## Repository hygiene

Only new files are added. Root `README.md` and `README_en.md` are untouched. Documentation is in `docs/phases/`.
