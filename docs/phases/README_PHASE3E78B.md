# Phase 3E-7.8B — Uniform arclength curvature comparison

Compares Euler S-Bend (AUTO) and CSC routes for the same ports, resampling their **centerline polylines** at 0.1 µm arclength intervals. No modification to router or GUI.

## Run

```bash
cd ~/Photonics/klayout-photonics-pdk
unzip -o ~/Downloads/Phase3E_7_8B_Uniform_Curvature.zip
klayout -b -r tests/test_route_curvature_uniform_v65.py
```

Outputs under `tests/phase3e78b_output/`:
- `auto_uniform_curvature.csv` and `csc_uniform_curvature.csv` (`s_um`, `x_um`, `y_um`, `kappa_per_um`)
- `summary.csv`
- `auto.gds`, `csc.gds`

## Plot (optional, requires matplotlib)

```bash
python3 tools/plot_uniform_curvature_v65.py
```

Output: `tests/phase3e78b_output/curvature_comparison.png`.

## Important limits

- Interpolation is piecewise linear on existing discretized centerlines. It does **not** reconstruct exact analytic Euler or CSC curvature.
- Three-point circumcircle curvature can show numerical spikes near polyline vertices, especially if the resampling step is not aligned with original segment lengths.
- `max_adjacent_delta_kappa_per_um` is a difference between neighboring samples, not the derivative `dκ/ds`.
- Equal sample spacing improves comparability, but this is not a foundry DRC or optical loss calculation.
- The test asserts the Euler S-Bend selection, not that Euler always beats CSC on any metric.
