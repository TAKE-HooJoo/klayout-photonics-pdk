# Phase 3E-7.8C-3: AUTO_QUALITY GUI registration

Adds a fourth toolbar tool (`AUTO_QUALITY`) to the existing KLayout Router v6.5 GUI generator. Keeps the existing `AUTO`, `CSC`, and `EULER` tools and the active-plugin click guard unchanged. **This phase does not display per-candidate scores**, because the existing `RouteResult` does not expose them.

## Installation

From `~/Photonics/klayout-photonics-pdk`:

```bash
unzip -o ~/Downloads/Phase3E_7_8C3_AUTO_QUALITY_GUI.zip
python3 tools/patch_router_v65_gui_quality.py
python3 -m unittest discover -s tests -p 'test_router_v65_quality_gui_build.py' -v
python3 tools/build_router_v65_gui.py
```

Check the generated macro contains `photonics_router_v6_5_auto_quality`, then install:

```bash
grep -n 'photonics_router_v6_5_auto_quality' pymacros/photonics_router_v6_5.lym
cp pymacros/photonics_router_v6_5.lym ~/.klayout/pymacros/
```

**Restart KLayout**. Select the `Photonics Router v6.5 AUTO_QUALITY` toolbar tool, click the source port, then the destination port. Confirm the result dialog reports `Mode: AUTO_QUALITY` and selected topology (e.g. `LSR` for the previous 80 µm × 15 µm test case).

## Regression checks

```bash
klayout -b -r tests/test_router_quality_v65.py
klayout -b -r tests/test_router_hybrid_v65_sbend.py
python3 -m unittest discover -s tests -p 'test_route_quality.py' -v
```

## Commit after GUI verification

```bash
git add tools/build_router_v65_gui.py pymacros/photonics_router_v6_5.lym \
  tools/patch_router_v65_gui_quality.py tests/test_router_v65_quality_gui_build.py README_PHASE3E78C3.md
git diff --cached --check
git commit -m "Add Phase 3E-7.8C-3 AUTO_QUALITY GUI tool"
git push origin main
```

The patcher backs up the original builder to `tools/build_router_v65_gui.py.before_quality.bak`; this backup should not be committed. Do not `git add .` because generated GDS and other untracked work may be present.
