# Phase 3E-7.1 — Sampled route quality diagnostics

This package adds **only** `photonics/routing/route_quality.py` and
`tests/test_route_quality.py`; it does not modify Router v6.4.

## Install

From the repository root, copy the two files into their matching directories.
Do not replace any existing `__init__.py` files.

## Run

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_route_quality.py' -v
```

## Use with an existing route

```python
from photonics.routing.route_quality import analyze_route
report = analyze_route(route.points, min_radius_um=5.0, turn_threshold_deg=5.0)
print(report)
```

Coordinates **must be micrometres**. If `route.points` are KLayout integer
`pya.Point` objects in database units, convert first:

```python
points_um = [(p.x * layout.dbu, p.y * layout.dbu) for p in route.points]
report = analyze_route(points_um)
```

`sharp_vertices` and `radius_violations` contain 1-based *interior point indices*.
`sampled_curvature` contains `(index, signed_curvature_1_per_um)` pairs.
Zero-length segments are reported rather than silently skipped.

## Interpretation

- A 3-point circumcircle radius is **not** an analytic bend radius.
- A small per-sample turn angle does **not** prove G1 continuity.
- CSC straight-to-arc transitions may be G1 while still having discontinuous curvature (not G2).
- This module does **not** check waveguide polygon self-intersections, exact GDS fidelity, or clearance; these require separate geometry-level tests.
