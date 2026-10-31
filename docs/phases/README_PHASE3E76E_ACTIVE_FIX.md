# Phase 3E-7.6E: active-plugin click dispatch fix

The observed log shows selected AUTO receives `prio=True`, while an inactive EULER instance receives `prio=False` and steals the click. This patch changes dispatch to check the last activated v6.5 plugin instance, not `prio`. Only that instance processes clicks. It does not change v6.4 or routing algorithms.

## Installation

From repository root, extract this ZIP. It replaces `tools/build_router_v65_gui.py` and `tests/test_router_v65_gui_build.py` only. Regenerate the v6.5 macro, run tests, then copy it into KLayout's macro folder:

```bash
python3 tools/build_router_v65_gui.py
python3 -m unittest discover -s tests -p 'test_router_v65_gui_build.py' -v
cp pymacros/photonics_router_v6_5.lym ~/.klayout/pymacros/
```

Completely close KLayout and launch from terminal:

```bash
klayout 2>&1 | tee /tmp/photonics_router_v65_active_fix.log
```

Select AUTO, then click source and destination. Check:

```bash
grep -E '\[v6\.5 (ACTIVATED|DEACTIVATED|CLICK|ROUTE|RESULT|EXCEPTION)\]' /tmp/photonics_router_v65_active_fix.log
```

Expected: `CLICK mode=AUTO prio=True` and `ROUTE mode=AUTO`. You may still see `CLICK mode=EULER prio=False` diagnostic lines, but no `ROUTE mode=EULER`. A failed AUTO may report CSC's `NO_CLEAR_WAYPOINT_ROUTE`, depending on geometry. This patch has NOT been tested in a running KLayout GUI.
