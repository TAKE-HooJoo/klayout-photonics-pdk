# Phase 3E-7.7A — Pure-Python Euler S-Bend

Adds `photonics/routing/euler_sbend.py`, preserving v6.4/v6.5 GUI and routing integrations.

This is **not yet GUI-integrated**. It supports equal travel headings, forward
travel and parallel lateral offsets, using two opposite symmetric Euler bends
with a straight lead on each end. `min_radius_um` is the design curvature
radius of the Euler bends; the sampled three-point radius can differ slightly.

The S-bend construction uses the existing `symmetric_euler_bend()` API from
Phase 3E-7.4, including its `.x`, `.y`, `.s` samples.

## Installation and test

```bash
cd ~/Photonics/klayout-photonics-pdk
unzip -o ~/Downloads/klayout_phase3e77a_euler_sbend.zip
python3 -m unittest discover -s tests -p 'test_euler_sbend.py' -v
```

## Example

```python
from photonics.routing.euler_sbend import route_euler_sbend
r = route_euler_sbend((0,0), (80,15), 0, 0, min_radius_um=6.25)
print(r.valid, r.reason, r.length_um, r.bend_angle_deg)
```

## Limitations

- Supports parallel **travel** headings, not 180-degree U-turns.
- No obstacle or DRC check. Do not insert directly into GDS; Phase 3E-7.7B
  must integrate with the v6.5 validation/clearance layer.
- Euler S-bend can fail if there is too little forward space for the offset.
- Does not perform an optimal-length search.
- Tests must be run against the user's existing Euler bend implementation.
