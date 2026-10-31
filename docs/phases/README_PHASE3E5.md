# Phase 3E-5: GDSII export and visualization

Adds a standalone GDS exporter without modifying existing Phase 3E-4 routing code.

## Installation

From the repository root:

```bash
unzip -n ~/Downloads/klayout_phase3e5_gds_visualization.zip -d .
```

## Test

```bash
klayout -b -r tests/test_klayout_route_gds.py
```

Expected: waypoint detour, GDS export, GDS round-trip/clearance, and Phase 3E-5 integration all PASS.

Generated GDS: `tests/phase3e5_output/waypoint_detour.gds`.
Open in KLayout using **File > Open**, or:

```bash
klayout tests/phase3e5_output/waypoint_detour.gds
```

Layers: 1/0 routed waveguide, 2/0 optical-port markers, 90/0 obstacle *visualization only*. The latter must not be interpreted as a foundry layer.

## Limitations

- Exact Region clearance against supplied obstacles is checked before write and after readback.
- Intended port geometry must be excluded/clipped by the caller before checking.
- Waypoint route's global self-spacing, self-intersection, detailed curvature, and foundry DRC are **not** verified here.
- The route's reported length is from the sampled centreline, not extracted from GDS polygons.
- The generated GDS is a **verification example**, not a tapeout-ready layout.

## Regression

```bash
klayout -b -r tests/test_klayout_waypoint_router.py
klayout -b -r tests/test_klayout_obstacle_router.py
klayout -b -r tests/test_klayout_clearance.py
```
