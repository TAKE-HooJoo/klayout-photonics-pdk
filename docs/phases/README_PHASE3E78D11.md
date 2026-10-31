# Phase 3E-7.8D-11: CSC theoretical junction and experimental quality sweep

## Scope

* Read-only analysis of prior Phase 3E-7.8D-7 CSV data.
* Ideal CSC model: circular arc has constant signed curvature ±1/R; straight has curvature 0. Tangent is continuous at the mathematically constructed CSC joins (G1), while curvature jumps by |1/R| (not G2).
* This **does not** independently verify tangent continuity of the *actual* router output. No CSC construction source or junction metadata is read.
* Euler `jump_inv_um=0` is accepted **only as an analytical model hypothesis**, informed by Phase 7.8D-10. The input CSV's historical `Euler_C1_UNVERIFIED` label is preserved and checked, not silently relabeled as a measured fact.
* All score weights are experimental geometric heuristics, not optical propagation loss.

## Run

```bash
cd ~/Photonics/klayout-photonics-pdk
python3 tests/test_csc_euler_quality.py
python3 tools/audit_csc_euler_quality.py
cat tests/phase3e78d11_output/ideal_csc_junctions.csv
cat tests/phase3e78d11_output/quality_weight_sweep.csv
```

Input files:
- `tests/phase3e78d7_output/integrated_score_experimental.csv`
- `tests/phase3e78d7_output/jump_radius_audit.csv`

Outputs:
- `tests/phase3e78d11_output/ideal_csc_junctions.csv`
- `tests/phase3e78d11_output/quality_weight_sweep.csv`

## Scoring

Within each case, deduplicate variants so that AUTO/CSC/AUTO_QUALITY returning the same LSR do not count as separate candidates. For each variant compute

`score = L/Lmin + Ew/Ewmax + Gmax/Gmaxmax + wJ*(Jr/Jrmax)`.

Zero maxima produce a zero term. Only cases with both Euler and CSC are genuine comparisons; offset cases with CSC only are not comparative evidence.

## Interpretation

The mathematical CSC model is G1 at tangent joins but not G2, with two jumps of magnitude 1/R. The CSV reports the *maximum* jump, not a sum of both. Real output junction positions and continuity must be audited against CSC source geometry separately. The Euler G2 analytical model does not prove the polygonal/GDS representation is G2.

No changes to the root README, routing engine, AUTO_QUALITY or GUI.
