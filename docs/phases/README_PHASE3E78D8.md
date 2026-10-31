# Phase 3E-7.8D-8 — Geometry audit

This phase adds **diagnostics only**. It does not modify the production router or AUTO_QUALITY.

## Install

Unzip from the repository root. This package does not include or overwrite root README.md.

## Run

```bash
cd ~/Photonics/klayout-photonics-pdk
python3 tests/test_route_geometry_audit.py
python3 tools/audit_route_geometry.py
```

Requires `tests/phase3e78d4_output/route_centerlines.csv`. If missing:

```bash
klayout -b -r tests/export_route_points_v65.py
```

Output: `tests/phase3e78d8_output/route_geometry_audit.csv`.

## Interpretation and limitations

- `inferred_arc_radius_um` is a median of local circumcircle radii selected near the **recorded designed radius**. It is a diagnostic of polygon samples, **not an independent proof** that the entire CSC arc or its junctions match the analytic geometry. An absent estimate is reported blank.
- `gradient_p95_inv_um2` is the 95th percentile of the **absolute fixed-window curvature gradient**.
- `gradient_l2_inv_um3` is the integral of the **squared fixed-window gradient** over the region with complete window support. Both are window-dependent; keep `half_window_um` fixed across comparisons.
- Polygon samples alone cannot prove Euler G2 continuity, nor accurately identify ideal curvature jumps at CSC line/arc junctions. Analytic primitive and junction metadata are needed before declaring `Euler Jr=0`.
- Compare sampling stability **within the same route and fixed window**, not scores across unrelated cases.
- Use a finer original source polyline or analytic geometry for a stronger radius audit. The curvature filter `[0.7/R, 1.3/R]` may bias the inferred radius toward the design target.
