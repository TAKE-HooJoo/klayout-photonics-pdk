# Phase 3E-7.8C-1 — Route quality evaluator

Independent pure-Python diagnostic engine. Does not modify Router v6.5 or KLayout macros.

## Install

From `~/Photonics/klayout-photonics-pdk`:

```bash
unzip -o ~/Downloads/Phase3E_7_8C1_Route_Quality.zip
python3 -m unittest discover -s tests -p 'test_route_quality.py' -v
```

## API

```python
from photonics.routing.route_quality import evaluate_route_quality
q = evaluate_route_quality([(0, 0), (5, 0), (10, 0)])
print(q)
```

Input points may be `(x, y)` tuples or objects exposing `.x`, `.y`. Units: um.

- `length_um`: sampled polyline length
- `max_abs_curvature_inv_um`: maximum signed circumcircle curvature magnitude at interior vertices
- `min_sampled_radius_um`: reciprocal of maximum curvature, or infinity for a straight route
- `curvature_energy_inv_um`: sampled sum of squared curvature times vertex dual-cell arc length
- `max_sampled_delta_curvature_inv_um`: maximum adjacent estimated curvature difference; depends strongly on sampling
- `max_declared_jump_inv_um`: maximum absolute curvature discontinuity supplied by caller via `curvature_jumps`; **not inferred** from a point sequence

For a CSC route, exact jumps must be obtained from its segment topology and supplied explicitly. Do not use `max_sampled_delta_curvature_inv_um` as a replacement for exact jump magnitude.

These are geometric diagnostics only, **not optical loss**, foundry DRC, or proof of curvature continuity. For comparing routes, resample to similar arc-length intervals before evaluating. The current energy estimator assumes zero endpoint curvature and is subject to endpoint and sampling errors. Do not use these values to rank production routes without convergence testing.

## Git

After tests pass:

```bash
git add photonics/routing/route_quality.py tests/test_route_quality.py README_PHASE3E78C1.md
git diff --cached --check
git commit -m "Add Phase 3E-7.8C-1 route quality evaluator"
git push origin main
```
