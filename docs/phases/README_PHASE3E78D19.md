# Phase 3E-7.8D-19: Exact CSC Parameter Reconstruction

## Scope

Read-only diagnostic of *direct* CSC paths selected by `route_between_ports_hybrid(..., mode='CSC')`. No Production router modifications. No KLayout layout changes beyond the standard single waveguide insertion by the existing Production router.

`dubins.words(alpha,beta,D/R)` supplies `(word,t,p,q)`, and `dubins.candidate(...)` builds the exact same sampled centerline. The diagnostic reproduces candidate generation and accepts parameters **only if** the entire returned point sequence matches within 1e-8 µm, with identical point count and variant. `samples_per_arc=36` is the current default in `route_avoiding_obstacles`. The match does not independently validate whether the Dubins solver formulas themselves are mathematically correct.

The formulas for a matched candidate are `L_arc=R*(t+q)`, `L_straight=R*p`, `L_total=R*(t+p+q)`, `E_curvature=(t+q)/R` and `jump=1/R`. `t,p,q` come from the original analytic candidate generator, not the polyline turning-angle proxy. For an LSR/RSL path, each straight/arc transition has a curvature jump of magnitude `1/R`; jump is not a gradient and is not optical loss.

## Run

```sh
cd ~/Photonics/klayout-photonics-pdk
python3 tests/test_phase3e78d19.py
klayout -b -r tests/run_phase3e78d19_klayout.py
cat tests/phase3e78d19_output/csc_exact_parameter_audit.csv
```

`NOT_MATCHED` is a legitimate diagnostic outcome: a waypoint-composite route, different arc sample count, or changed router behavior must not be labeled exact. The CSV leaves analytic fields empty if the match fails. Empty obstacle-free test layouts are used. A 1e-8 µm match is a strict numerical provenance check, not a proof of GDS-level equivalence or foundry DRC signoff.
