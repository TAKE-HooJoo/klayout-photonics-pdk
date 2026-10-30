# Phase 3E-7.8C-2 — AUTO_QUALITY (experimental)

This package adds `AUTO_QUALITY` to `router_hybrid_v65.py` while preserving CSC/EULER/AUTO selection and validation. It evaluates all validated candidates and inserts only the selected route.

## Install

```bash
cd ~/Photonics/klayout-photonics-pdk
unzip -o ~/Downloads/Phase3E_7_8C2_AUTO_QUALITY.zip
klayout -b -r tests/test_router_quality_v65.py
```

**Important:** The ZIP also includes the existing `route_quality.py` solely as a reference; it is NOT necessary to overwrite the committed Phase 3E-7.8C-1 file. Inspect the diff before installation or use `unzip -o ... photonics/integration/router_hybrid_v65.py tests/test_router_quality_v65.py README_PHASE3E78C2.md` to install only new/modified files.

Score = `L/L_min + E/E_max`, where `E` is the sampled curvature-squared integral. If `E_max=0`, its term is zero. This is a provisional geometry heuristic, not an optical-loss model. Curvature jumps are not included because CSC topology metadata is not available. Sampling density differs across candidates, so results require further validation.

Run the existing regression tests too:

```bash
klayout -b -r tests/test_router_hybrid_v65_sbend.py
klayout -b -r tests/test_router_hybrid_v65_klayout.py
python3 -m unittest discover -s tests -p 'test_route_quality.py' -v
```

Do not commit generated GDS/output directories. Review `git diff` and commit only the router, new test and README after PASS.
