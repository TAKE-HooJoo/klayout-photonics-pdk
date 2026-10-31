# Phase 3E-7.7B — KLayout Euler S-Bend integration

This package **adds** `photonics/integration/router_euler_sbend.py` and `tests/test_euler_sbend_klayout.py`. It does not modify v6.5 GUI, hybrid router, or the Phase 3E-7.7A solver.

## Install

From `~/Photonics/klayout-photonics-pdk`:

```bash
unzip -o ~/Downloads/klayout_phase3e77b_euler_sbend_klayout.zip
python3 -m unittest discover -s tests -p 'test_euler_sbend.py' -v
klayout -b -r tests/test_euler_sbend_klayout.py
```

Output GDS files are written to `tests/phase3e77b_output/` (do not automatically commit generated GDS files).

## API

```python
route_euler_sbend_klayout(cell, layout, source, destination,
    source_heading_deg, destination_heading_deg,
    waveguide_layer=(1,0), width_um=0.5, min_radius_um=6.25,
    obstacle_region=None, obstacle_layer=None, clearance_um=0.0,
    samples_per_bend=201, tangent_tolerance_deg=5.0,
    radius_tolerance_fraction=0.02)
```

All coordinates in µm. Both headings describe **travel direction**, not outward device port direction. To use an outward-facing destination port direction, add 180° to obtain the arrival travel heading. The supplied obstacle region uses integer KLayout DBU coordinates. The optional keepout layer is never clipped at endpoints. The adapter only inserts geometry after validation. Existing waveguide geometry is **not** automatically collected as obstacles. Endpoint overlap windows are not supported by this standalone adapter.

### Validation limitations

Sampled circumcircle radius is an approximation and may not constitute continuous-curvature verification or fabrication DRC. The test confirms the basic obstacle rejection and nonmutation behavior, not complete photonic connectivity or manufacturing sign-off. Polygon discretization and quantization are not checked with a full post-GDS DRC. Check results in KLayout before integration into AUTO.

## Git

```bash
git add photonics/integration/router_euler_sbend.py tests/test_euler_sbend_klayout.py README_PHASE3E77B.md
git diff --cached --check
git commit -m 'Add Phase 3E-7.7B Euler S-bend KLayout integration'
git push origin main
```
