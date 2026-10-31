# Phase 3E-7.8D-10 — Euler analytical junction audit

## Scope

This independent diagnostic imports the **existing** `symmetric_euler_bend` and `route_euler_sbend` functions. It does not edit routing, layout, or the root README files.

For the continuous Euler model, curvature varies linearly 0 → ±1/R → 0. The S-bend reflects and rotates the first bend to form the second. At each of the three joins (lead/first, first/second, second/lead), the continuous model has matching tangent and zero curvature on both sides, hence G1 and G2 at these joins. This is a source-aware *model-level* audit, not an independent symbolic proof of every polygonal segment.

The finite sampled polyline has vertex turns and does **not** possess classical G2 curvature at vertices. A sampled maximum turn is reported as a discretization diagnostic. CSC junctions are not checked by this tool; a separate audit of the CSC generator is required.

## Usage

From repository root:

```bash
python3 tests/test_euler_analytic_audit.py
python3 tools/audit_euler_analytic.py
cat tests/phase3e78d10_output/euler_analytic_audit.csv
```

Optional: `--samples 401 --radius 6.25`.

## Interpretation

- `max_heading_jump_deg` and `max_curvature_jump_inv_um` are **continuous-model** join values derived from the source transformation, not numerically reconstructed polygon joins.
- `analytic_peak_curvature_inv_um` is 1/R; it is not the sampled maximum curvature.
- `analytic_min_radius_um` is the continuous Euler model radius, not a fabrication signoff.
- A result of PASS in unit tests is not proof of optical loss, foundry DRC, or G2 of the discretized GDS polygon.

## Future

Inspect CSC tangent/junction implementation separately; quantify join-coordinate mismatch under sample refinement and verify the KLayout polygon output.
