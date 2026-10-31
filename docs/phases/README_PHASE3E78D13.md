# Phase 3E-7.8D-13: Production Router vs Historical Shadow v2

## Scope
Run **actual** KLayout production routing in separate fresh layouts for AUTO_QUALITY, CSC and EULER. Verify valid candidates insert one shape, failed routes insert none. Compare the AUTO_QUALITY winner with the **previously saved offline Phase 12 shadow winner** at a selected jump weight.

**Important:** This is NOT a live shadow evaluation of all production candidates. Phase 12 data was derived from a historical candidate set, which can differ from the current KLayout run. A match/mismatch is descriptive, not pass/fail or evidence of equivalent candidate sets. Production router source and scoring are never modified. No optical loss or GDS G2 claims.

## Run from repository root

```bash
python3 tests/test_production_shadow_compare.py
klayout -b -r tests/run_phase3e78d13_klayout.py
python3 tools/compare_production_shadow_v2.py --weight-jump 1
cat tests/phase3e78d13_output/production_routes.csv
cat tests/phase3e78d13_output/production_shadow_comparison.csv
```

Requires `tests/phase3e78d12_output/shadow_quality_comparison.csv` from Phase 12.

## Follow-up for true live shadow parity

Capture all *accepted* candidates within the same router invocation, before placement, then evaluate v2 on their centerlines using common resampling, curvature windows and independently verified analytic junction metadata. This requires a carefully isolated diagnostic adapter and dedicated integration tests; this phase does not claim to implement it.
