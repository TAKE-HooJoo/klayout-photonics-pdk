# Phase 3E-1 — Conservative obstacle screening (prototype)

This additive prototype does not modify the existing router.

## Install

From the project root:

```bash
unzip -o ~/Downloads/klayout_phase3e1_obstacles.zip -d .
python3 -m unittest discover -s tests -p 'test_obstacles.py' -v
```

Adjust the ZIP location as needed. The pure-Python tests use the project's
existing `photonics.circuit.geometry.Point`.

## Example

```python
from photonics.routing.obstacles import Obstacle, detect_obstacles
hits = detect_obstacles(result.points, cross_section.width_um,
                        design_rules.min_waveguide_spacing_um,
                        (Obstacle(4, -1, 6, 1),))
print(hits)
```

## Limitations

* Bounding-box screening, NOT polygon-accurate DRC. It can produce false positives.
* The spacing buffer assumes obstacle bounding boxes already include the full
  obstacle waveguide width. If you supply centerlines instead, expand them first.
* The `ignored_owners` option skips an entire obstacle. Do not use this for
  general endpoint connectivity verification; a port-local exclusion is needed.
* `extract_waveguide_obstacles` is intended for KLayout batch/GUI execution and
  has not been validated in KLayout in this package. Verify recursive iterator
  transforms and output with a real PCell hierarchy before integration.
* No automatic rerouting, exact polygon checks, or port connectivity checks yet.
