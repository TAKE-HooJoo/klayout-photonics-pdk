# Phase 3E-7.6A — Endpoint-constrained Euler route (prototype)

This module implements a **single ±90°** Straight–Euler–Straight route with fixed optical-port positions and directions. It reuses `photonics/routing/euler_bend.py` from Phase 3E-7.4 and does not modify Router v6.4.

The Euler curve has linearly increasing/decreasing curvature (zero at both ends) and a peak curvature `1/min_radius_um`. Two nonnegative straight leads are calculated analytically in the source-heading coordinate system. The solver returns `valid=False` with `INSUFFICIENT_LEAD_SPACE` if the bend does not fit, or `UNSUPPORTED_TURN_ANGLE` for other turn angles. No radius violation is silently allowed.

## Install and test

From the repository root:

```bash
unzip ~/Downloads/klayout_phase3e76a_endpoint_euler.zip
PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_euler_endpoint_solver.py' -v
```

## Example

```python
from photonics.routing.euler_endpoint_solver import route_straight_euler_straight
r = route_straight_euler_straight((0, 0), (30, 30), 0, 90, min_radius_um=6.25)
print(r.valid, r.reason, r.length_um, r.endpoint_error_um)
```

## Scope and limitations

- Supports a single left/right quarter-turn, not arbitrary port orientations or multi-bend paths.
- Endpoint matching is evaluated numerically; sampled polyline vertices do not prove exact G1/G2 geometry, although the underlying Euler formula is curvature-continuous at straight joins.
- No obstacle checking, GDS export, width polygonization or PDK DRC in this phase.
- If source/destination are too close, the solver correctly rejects the route instead of shrinking the bend below the minimum radius.
- A ±90° angle difference is treated as a quarter-turn only within the configured heading tolerance.

Next: Phase 3E-7.6B KLayout GDS/clearance verification and, subsequently, a more general solver for arbitrary port pairs.
