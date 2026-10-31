# Phase 3E-7.8D-18 — CSC analytic parameter provenance audit

## Scope
This is a read-only diagnostic. It does not alter Production `AUTO_QUALITY`, candidate selection, or router source.

## What it verifies
- Exact analytic energy formula for explicitly supplied CSC parameters: `(arc1_rad + arc2_rad) / radius_um`.
- Whether the production route result **exposes** arc1_rad, arc2_rad, straight_um.
- If not exposed, exact analytic energy is left blank; the Phase 17 polyline turning proxy is shown separately.
- Locates public router functions for a follow-up source-level integration.

## What it does not verify
It does not reconstruct exact CSC primitive parameters from generated polygons, and cannot prove analytic energy without access to the underlying CSC solver parameters. Do not label polyline-derived values as exact.

## Run
```bash
cd ~/Photonics/klayout-photonics-pdk
python3 tests/test_phase3e78d18.py
klayout -b -r tests/run_phase3e78d18_klayout.py
cat tests/phase3e78d18_output/csc_parameter_provenance.csv
cat tests/phase3e78d18_output/source_locations.csv
```

## Next step
If `EXACT_PARAMETERS_NOT_EXPOSED`, inspect `photonics/routing/engine.py` and the actual CSC solver output; add an **optional diagnostic metadata interface** without changing the route geometry or production scoring. Requires source inspection first.
