# Phase 3E-2: KLayout Region clearance screening

This additive implementation does not modify Router v6.3 or Phase 3E-1.

## Install

From repository root, unzip the package into the repository. Run:

```bash
klayout -b -r tests/test_klayout_clearance.py
python3 -m unittest discover -s tests -p 'test_obstacles.py' -v
```

## Limitations

- Clearance is conservatively screened using integer-DBU dilation (`Region.sized`) and intersection. It is not a foundry sign-off DRC and can over-report near grid boundaries or corners.
- The route and obstacle regions must be **distinct**. Do not include the new route in the obstacle region.
- Optical pin regions are not extracted. Intended port connections must be excluded or geometrically clipped explicitly; never exempt an entire device without checking other collisions.
- This module does not auto-route around obstacles or insert shapes into the layout.
- The KLayout integration test needs to be executed in the user's KLayout installation; it has not been run in this packaging environment.
