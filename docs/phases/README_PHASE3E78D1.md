# Phase 3E-7.8D-1 Route Quality Benchmark

No production router code is modified. Each mode is evaluated on a fresh KLayout cell to prevent previously inserted waveguides from becoming obstacles.

Run from the repository root:

```bash
klayout -b -r tests/test_route_quality_benchmark_v65.py
```

Outputs: `tests/phase3e78d1_output/route_quality_benchmark.csv` and one GDS per successful case/mode.

Cases: (0,0) to (80,15) and (120,25), both facing optical ports. Modes: AUTO, CSC, EULER, AUTO_QUALITY.

`relative_score` is a cross-mode *diagnostic*, using the valid routes exposed by these modes. It is **not guaranteed** to match the internal AUTO_QUALITY candidate ranking, which can include additional accepted candidates. Curvature metrics are sampled geometry diagnostics, not optical propagation loss.

Do not commit generated GDS files unless explicitly desired. The test has not been executed under KLayout in the packaging environment; run it on the target machine and report failures.
