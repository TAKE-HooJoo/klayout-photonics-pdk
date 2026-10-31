# Phase 3E-4 — Waypoint-based obstacle avoidance (experimental)

Adds `photonics/integration/obstacle_router_v2.py` **without replacing** the
Phase 3E-3 module or Router v6.3 GUI. First tries the existing straight/CSC
route; if blocked, tries two offset waypoints above/below the port-to-port
chord, with forward-facing tangent continuity. Each leg is checked using the
existing KLayout Region clearance checker; the combined route is checked again.

## Install

```bash
cd ~/Photonics/klayout-photonics-pdk
unzip -n ~/Downloads/klayout_phase3e4_waypoint_router.zip -d .
python3 -m py_compile photonics/integration/obstacle_router_v2.py tests/test_klayout_waypoint_router.py
klayout -b -r tests/test_klayout_waypoint_router.py
klayout -b -r tests/test_klayout_obstacle_router.py
```

## Limitations

- The waypoint search is heuristic, not complete. Failure means no candidate
  passed this search, not that no physical route exists.
- Only a small bounded set of offset waypoints is explored.
- Intended port-connected shapes must be excluded/clipped from obstacle Region.
- Does not implement self-spacing DRC, precise polygonal curvature verification,
  obstacle extraction in this adapter, or GUI integration.
- Sampled arcs are polygonal approximations; final foundry DRC is required.
- The KLayout integration test should be run on the user's local KLayout;
  Python syntax and ZIP checks alone do not establish runtime correctness.
