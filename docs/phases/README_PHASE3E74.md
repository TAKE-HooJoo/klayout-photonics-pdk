# Phase 3E-7.4 — Euler Bend prototype

A standalone, KLayout-independent symmetric Euler/clothoid bend generator.

## Files

- `photonics/routing/euler_bend.py`: sampled centerline and analytical curvature/heading
- `tests/test_euler_bend.py`: unit tests

## Run

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_euler_bend.py' -v
```

## Model

For target turn angle `A` (radians) and minimum radius `R`, the total arc length is `L=2|A|R`. Curvature ramps linearly from 0 to `sign(A)/R` at `s=L/2`, then back to 0 at `s=L`. The tangent heading is obtained by integrating curvature analytically; XY coordinates integrate the unit tangent using Simpson quadrature. Endpoint tangent rotation is `A`. The curve is G2-compatible with straight leads (zero endpoint curvature).

**Limitations:** This is a geometric prototype, not a drop-in CSC replacement. Its endpoint displacement differs from a circular bend. Do not replace existing routes without solving endpoint/heading constraints and rechecking obstacles, waveguide width, self-intersections, and fabrication design rules. Numerical sampling does not constitute a foundry-level optical-loss verification.
