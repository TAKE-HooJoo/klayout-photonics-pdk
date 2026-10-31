# Phase 3E-6: Photonics Router v6.4 (experimental)

## Scope

- Keeps `pymacros/photonics_router_v6_3.lym` unchanged.
- Reuses v6.3 native PCell port selection and two-click GUI.
- Calls Phase 3E-4 `route_with_waypoints` with hierarchical waveguide Region obstacles.
- Validates route tangent, sampled radius, sharp turns and Region clearance **before inserting** geometry on 1/0.
- Displays topology, length, radius and port tangent errors.
- Uses a small square **port connection window** at each endpoint to exclude device waveguide geometry from the obstacle Region. This is an experimental assumption, not full device-aware PDK verification.

## Install

From the repository root:

```bash
unzip -n ~/Downloads/klayout_phase3e6_router_v64.zip -d .
python3 -m py_compile photonics/integration/router_v64.py
klayout -b -r tests/test_router_v64_klayout.py
```

If the KLayout test passes, copy the macro into KLayout's macros directory:

```bash
cp pymacros/photonics_router_v6_4.lym ~/.klayout/pymacros/
```

Restart KLayout, choose the **Photonics Router v6.4** tool and click source and destination optical ports. If both v6.3 and v6.4 are registered, select v6.4 explicitly. The plugin does not modify the layout if the candidate fails checks.

## Known limitations

- No complete foundry DRC or optical mode transition verification.
- Port window is a deliberately small geometric exemption; connection to the PCell device must be inspected and verified separately.
- Sampled three-point radius and sampled turn angle are diagnostics, not a rigorous bound on continuous curvature.
- Region-based clearance does not cover self-spacing of a single routed waveguide.
- Routes are inserted as polygons. The v6.3 netlist extractor, which only collects `Path` shapes, may not recognize these connections. Netlist extraction must be upgraded before production use.
- Plugin GUI operation must be tested on the user's KLayout 0.30.9 installation; only syntax/package validation was available when the ZIP was built.
- The macro preserves the v6.3 `_PDK_ROOT` absolute path (`/home/take/Photonics/klayout-photonics-pdk`); adjust if installed elsewhere.

## Git

Stage only the new files, not generated outputs or unrelated untracked files:

```bash
git add pymacros/photonics_router_v6_4.lym photonics/integration/router_v64.py tests/test_router_v64_klayout.py README_PHASE3E6.md
git diff --cached --check
git commit -m 'Add experimental obstacle-aware Photonics Router v6.4 GUI'
git push
```
