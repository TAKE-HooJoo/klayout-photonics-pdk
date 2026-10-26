# Phase 3E-7.2 — Real-route quality diagnostics

This adds a **read-only diagnostic test** for the existing Router v6.4 waypoint detour.
No routing or GUI implementation is modified.

## Run

```bash
cd ~/Photonics/klayout-photonics-pdk
klayout -b -r tests/test_route_quality_klayout.py
```

The test creates a fresh KLayout layout, inserts a 6 × 6 µm waveguide-layer
obstacle at x=37–43 µm, y=-3–3 µm, and connects ports at (0,0) and (80,0).
It verifies the returned WAYPOINT_CSC route, absence of sampled radius violations
and sharp vertices, and clearance against the original obstacle. It writes
`tests/phase3e72_output/route_curvature.csv` for plotting or analysis.

The CSV contains vertex index, cumulative path distance, coordinates, signed
sampled curvature, and corresponding 3-point radius. Endpoints have no
three-point curvature. A zero curvature corresponds to infinite radius.

**Limitations:** sampled turn and 3-point circumcircle curvature do not prove
mathematical G1/G2 continuity. A sudden curvature change at a straight–arc
join can exist even when the sampled turn angles are small. This test does
not alter geometry or claim foundry-rule compliance.

Do not commit generated CSV unless it is intentionally needed as a fixture.
