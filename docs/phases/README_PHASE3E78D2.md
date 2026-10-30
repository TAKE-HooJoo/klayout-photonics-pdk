# Phase 3E-7.8D-2: Route quality benchmark plots

This package does not overwrite the repository root `README.md`.

```bash
cd ~/Photonics/klayout-photonics-pdk
unzip -o ~/Downloads/Phase3E_7_8D2_Quality_Plots.zip
python3 tests/plot_route_quality_benchmark_v65.py
```

Input: `tests/phase3e78d1_output/route_quality_benchmark.csv`.
Output: `tests/phase3e78d2_output/*.png` (up to eight plots).
Requires Python 3 and matplotlib. No KLayout invocation is needed for plotting.

Notes: The `relative_score` column is the benchmark's score, not necessarily the internal AUTO_QUALITY candidate score. Sampled curvature energy and max delta depend on sampling; they are not optical loss. The CSV does not include kappa(s) point series.
