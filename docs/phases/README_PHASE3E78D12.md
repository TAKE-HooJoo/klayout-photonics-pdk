# Phase 3E-7.8D-12 — Offline Shadow Quality v2

## Purpose
Read Phase 3E-7.8D-11 `quality_weight_sweep.csv`, recompute its four-term geometric score independently, verify winners and output a shadow comparison. **This is an offline replay of historical candidate data, not live parallel routing, not a change to AUTO_QUALITY, and not optical loss prediction.**

## Installation
From the repository root, unzip this package. It only adds `tools/shadow_quality_v2.py`, `tests/test_shadow_quality_v2.py` and this documentation. Root README files and router code are not modified.

## Run
```bash
python3 tests/test_shadow_quality_v2.py
python3 tools/shadow_quality_v2.py
cat tests/phase3e78d12_output/crossover_summary.csv
head -n 15 tests/phase3e78d12_output/shadow_quality_comparison.csv
```

Input: `tests/phase3e78d11_output/quality_weight_sweep.csv` (required).
Outputs: `tests/phase3e78d12_output/shadow_quality_comparison.csv` and `crossover_summary.csv`.

## Limitations
- Reported prior winners are from the Phase 11 experimental CSV, **not** production AUTO_QUALITY decisions. Thus parity verifies reproducibility, not production behavior.
- Input normalized values are case/candidate-set specific; scores across cases are not comparable.
- Euler G2 and ideal CSC jumps are analytic-model assumptions; not GDS proof.
- The crossover depends on fixed baseline candidate set and `wL=wE=wG=1`.
- Next phase: capture live production selection separately, then compare shadow choices without changing router selection.
