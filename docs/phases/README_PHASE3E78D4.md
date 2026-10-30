# Phase 3E-7.8D-4: common-arc-length curvature evaluation

No changes to production Router, PCell, or root README.md.

```bash
cd ~/Photonics/klayout-photonics-pdk
unzip -o ~/Downloads/Phase3E_7_8D4_Curvature_Stability.zip
klayout -b -r tests/export_route_points_v65.py
python3 tools/analyze_curvature_sampling.py
```

Output: `tests/phase3e78d4_output/route_centerlines.csv`, `curvature_sampling_sweep.csv`.

For each successful route, resamples at requested spacing 0.5, 0.25, 0.1, 0.05 um and computes sampled curvature energy, sampled max delta curvature, max abs curvature. The true uniform spacing is slightly smaller than the requested spacing to preserve endpoints. Values depend on original polygonal sampling and resampling, and do not constitute exact analytic curvature or optical loss. The `csc_nominal_jump_proxy_inv_um` column is **1/designed radius** only for recognizable CSC topology labels; it is a theoretical proxy, not an extracted topology-exact jump. Do not confuse it with max sampled delta curvature. Compare trends across sampling steps; no unconditional convergence claim.

Expected: two cases, four modes; invalid EULER routes are omitted. 7 valid route rows x 4 steps = 28 records if earlier benchmarks reproduce.
