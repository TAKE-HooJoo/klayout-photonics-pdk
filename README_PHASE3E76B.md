# Phase 3E-7.6B — KLayout endpoint-constrained Euler validation

Independent integration test; does **not** modify Router v6.4.

## Run

From `~/Photonics/klayout-photonics-pdk`:

```bash
klayout -b -r tests/test_euler_endpoint_klayout.py
klayout tests/phase3e76b_output/euler_endpoint_90deg.gds
```

## Design

- Source `(0,0)` heading `0°`, destination `(40,40)` heading `90°`.
- `route_straight_euler_straight` from Phase 3E-7.6A; minimum design bend radius `6.25 µm`; waveguide width `0.5 µm`.
- GDS: waveguide `1/0`, port markers `2/0`, example obstacle `90/0`.
- CSV: sampled route centerline coordinates.
- Asserts: solver validity, source/destination position and sampled heading tolerance, sampled three-point bend radius, clearance from one nonblocking rectangular obstacle, and rejection of one blocking rectangular obstacle.

## Important limitations

- The obstacle test is **collision validation only**, not rerouting. It uses straight line segments between sampled centerline points against axis-aligned obstacle rectangles expanded by half the waveguide width. This is conservative for the *polyline approximation*, but does not mathematically certify the continuous curve between samples or arbitrary-shaped obstacles.
- The three-point radius is a **sampled diagnostic**, not a rigorous global curvature bound. A `0.05 µm` numerical tolerance is used for the sampled radius assertion.
- GDS coordinates are quantized to a `0.001 µm` database unit.
- Only the solver's currently supported single ±90° Euler bend is tested. No claim of optical loss, G2 continuity of fabricated polygons, or v6.4 router integration.
- The script requires KLayout's Python `pya` module and existing `photonics.routing.euler_bend` and `euler_endpoint_solver` modules.

## Git

```bash
git add tests/test_euler_endpoint_klayout.py README_PHASE3E76B.md
git diff --cached --check
git commit -m "Add Phase 3E-7.6B KLayout Euler endpoint validation"
git push origin main
```

Generated `tests/phase3e76b_output/` files are intentionally not staged.
