# Phase 3E-7.8D-9 — Junction polyline audit

## Purpose

Verify the **sampled** maximum curvature, approximate minimum radius and local vertex turning of the existing route centerlines. This is a prerequisite diagnostic for a later analytic G1/G2 proof. No Router, GUI, or AUTO_QUALITY changes.

## Install

From the repository root, extract the ZIP preserving paths. The Phase D-4 CSV exporter and Phase D-5/D-8 helper scripts must already be present.

```bash
python3 tests/test_route_junctions.py
python3 tools/audit_route_junctions.py
```

Output: `tests/phase3e78d9_output/junction_polyline_audit.csv`.

## Interpretation

- `max_sampled_abs_curvature_inv_um` is the maximum circumcircle curvature over original vertices. It is **not** a proven bound on the underlying continuous path.
- `min_sampled_radius_um` is its reciprocal, not a certified minimum bend radius.
- `max_vertex_turn_deg` is the angle between consecutive polygon edges, **not** a G1 junction tangent error.
- `arc_like_samples` counts vertices with curvature within 25% of 1/R; Euler curves do not have a constant curvature arc, so this count is not an Euler quality metric.
- `sampled_radius_constraint` uses a 1% numerical allowance; it does not establish a DRC pass.
- A G1/G2 proof requires the router's segment metadata, analytic formulas, and exact segment boundary positions. A CSV of sampled points cannot prove it. In particular, do not assign Euler Jr=0 merely because its vertex turns are small.

## Next investigation

Inspect the Euler generator's source and parameterization. Export per-segment metadata (type, start/end arc length, endpoint tangent and endpoint curvature) from the router; then evaluate G1 and G2 directly at each junction. CSC straight-to-arc transitions are expected to have a curvature jump of 1/R if ideal tangent arcs are used.
