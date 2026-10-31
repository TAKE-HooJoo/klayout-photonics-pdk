# Phase 3E-7.6E GUI debug build

Replaces only the v6.5 GUI generator and its unit test. The v6.4 macro and hybrid routing adapter remain untouched.

```bash
cd ~/Photonics/klayout-photonics-pdk
unzip -o ~/Downloads/klayout_phase3e76e_gui_debug.zip
python3 tools/build_router_v65_gui.py
python3 -m unittest discover -s tests -p 'test_router_v65_gui_build.py' -v
cp pymacros/photonics_router_v6_5.lym ~/.klayout/pymacros/
# Completely quit any running KLayout before launching this:
klayout 2>&1 | tee /tmp/photonics_router_v65_debug.log
```

Select AUTO, click source and destination, then inspect:

```bash
grep -E '\[v6\.5 (ACTIVATED|DEACTIVATED|CLICK|ROUTE|RESULT|EXCEPTION)\]' /tmp/photonics_router_v65_debug.log
```

Look for instance ID and mode at activation and click. The debug build does not change route selection behavior; it diagnoses plugin event delivery. If KLayout was already running, use the terminal launching the actual GUI process.
