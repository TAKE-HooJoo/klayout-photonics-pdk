# Phase 3E-7.8D-14 — Live Shadow Quality v2

This is a **non-invasive runtime observation** of accepted AUTO_QUALITY candidates.

- Temporarily wraps `router_hybrid_v65.evaluate_route_quality`, capturing the same accepted candidate centerlines that production evaluates; always restores the function in `finally`.
- Identifies candidates by matching point coordinates to independent CSC/EULER calls. This assumes deterministic candidate generation and an empty obstacle environment. Unmatched/ambiguous candidates fail closed.
- Production retains its original quality score and placement; shadow computes a separate 4-term score (length, fixed-window sampled curvature energy, sampled gradient maximum, ideal model junction jump).
- Euler ideal jump is 0; CSC ideal jump is `1 / designed_radius`. These are **analytic model assumptions**, not measured GDS discontinuities.
- Fixed-window proxies are sampling-sensitive and are **not** measured optical losses.
- Production and shadow winners may differ without failing the test.
- This phase does not verify GDS polygon G2 continuity or foundry DRC.

## Run from repo root

```bash
unzip -o ~/Downloads/Phase3E_7_8D14_Live_Shadow_v2.zip
python3 tests/test_live_shadow_quality_v2.py
klayout -b -r tests/run_phase3e78d14_klayout.py
cat tests/phase3e78d14_output/live_comparison.csv
cat tests/phase3e78d14_output/live_candidate_scores.csv
```

The test runner assumes the existing `photonics` package, KLayout `pya`, and production router modules are available. No production source is modified. The `tools` directory can be a namespace package on modern Python.
