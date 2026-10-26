# Phase 3E-7.6C — Experimental CSC / Euler / Auto Selector

This phase adds an independent pure-Python route selector. It **does not modify** Router v6.4 or place GDS geometry.

## Files
- `photonics/routing/hybrid_route_selector.py`
- `tests/test_hybrid_route_selector.py`

## Modes
- `EULER`: use existing Phase 3E-7.6A endpoint solver only; invalid geometry is rejected.
- `CSC`: invoke injected `csc_router` callback only; absent callback is rejected.
- `AUTO`: try Euler first, then CSC if Euler fails geometry or clearance validation.

## Usage
```python
from photonics.routing.hybrid_route_selector import select_route
r = select_route((0, 0), (40, 40), 0, 90, mode='EULER')
assert r.valid and r.mode == 'EULER'
```

Run tests:
```bash
PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_hybrid_route_selector.py' -v
```

## Safety and limits
- No GDS placement occurs in this module.
- The optional `clearance_check(points)` must be connected to the **actual** KLayout geometry/width-aware collision validator before placement. Without it, obstacle clearance is **not** checked.
- Only endpoint positions are checked for CSC callback output. CSC tangent and minimum-radius constraints must be validated by its own implementation or a future shared validator before placement.
- CSC callback API is deliberately injected because the repository's actual v6.4 API has not been inspected.
- Euler is restricted to the existing solver's single ±90° bend.
- `AUTO` is a policy selector, not a general path search algorithm.
