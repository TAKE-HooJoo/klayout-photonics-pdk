# Phase 3E-7.6D — Hybrid CSC/Euler KLayout Integration

Experimental integration alongside v6.4. Does **not** edit existing router files.

## Install

Extract this archive at the repository root, preserving directories.

## Run

```bash
cd ~/Photonics/klayout-photonics-pdk
klayout -b -r tests/test_router_hybrid_v65_klayout.py
```

Generated GDS: `tests/phase3e76d_output/hybrid_{euler,auto,csc}.gds`.

## Behavior

- EULER: endpoint-constrained 90° Straight–Euler–Straight.
- CSC: existing `route_with_waypoints` including obstacle detours.
- AUTO: Euler first, CSC on failure.
- Every candidate is checked for endpoints, tangents, sampled radius, sharp corners, spacing and overlap before a **single** insertion.
- Existing WG obstacles are clipped only in small endpoint connection windows; dedicated 90/0 keepouts are never clipped.
- Failure returns `RouteResult(valid=False)` and leaves WG shapes unchanged.

## Limitations

- No GUI plugin added; invoke from Python/KLayout scripts.
- Euler supports only +/-90° with nonnegative straight leads.
- Sampled radius and region spacing are screening checks, not signoff DRC.
- Existing waypoint search is heuristic, not complete.
- Connection-window WG clearance exemption is not a foundry DRC waiver.
- Source/destination `direction` values must be **outward** from devices.
- The module performs geometry placement only after selection, so don't call the v6.4 mutating `route_between_ports_v64` as a fallback callback.
