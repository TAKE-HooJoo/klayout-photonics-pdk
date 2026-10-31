# Phase 3E-7.8D-17 — CSC turning-angle energy proxy audit

This is a **diagnostic only**, not a modification to production AUTO_QUALITY.

## Model

For an ideal CSC with constant signed curvature ±1/R on circular arcs and zero on straights:

- `E = sum(L_arc)/R² = sum(abs(theta_arc))/R`
- Ideal curvature jump magnitude at each straight/arc boundary is `1/R`.

The exact arc angles and boundaries are **not available** in the Phase 14 observer callback. This package estimates total absolute turning from successive polyline segment headings. Thus `ideal_energy_proxy_inv_um` is a **polyline-derived proxy**, not a verified exact analytic energy. It can undercount arc turning by approximately one angular sample per arc and may count artifacts. It is independent of *evaluation ds* but dependent on the original CSC centerline discretization.

The old `centerline_metrics` energy is a fixed-window smoothed numeric diagnostic; comparing it to the ideal unsmoothed model combines smoothing bias and discretization error. Do not interpret the relative difference as numerical integration error alone. The fixed physical span Phase 16 metric is not included because its source was not provided; do not claim this package compares Phase 16 outputs.

## Run

```bash
cd ~/Photonics/klayout-photonics-pdk
unzip -o ~/Downloads/Phase3E_7_8D17_CSC_Energy_Audit.zip
python3 tests/test_phase3e78d17.py
klayout -b -r tests/run_phase3e78d17_klayout.py
cat tests/phase3e78d17_output/csc_energy_audit.csv
```

Requires Phase 14 `tools/live_shadow_quality_v2.py`, KLayout and `router_hybrid_v65`.

## Follow-up

For an exact analytic benchmark, expose CSC arc angles/segment types from the routing engine without changing geometry, or derive them from the original CSC solution parameters; then evaluate `sum(abs(theta_arc))/R` and compare at a fixed smoothing convention.
