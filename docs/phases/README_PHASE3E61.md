# Phase 3E-6.1 — 90/0 dedicated obstacle layer

This patch updates the existing Router v6.4. It does **not** change the v6.3 macro.

- `1/0`: existing waveguide geometry (endpoint connection windows are exempted as in v6.4).
- `90/0`: dedicated keepout/obstacle polygons, recursively collected from the active cell. **No endpoint-window exemption** applies to these polygons.
- `2/0`: optical pin layer (unchanged).

Only the waveguide `1/0` layer receives newly generated geometry. If `90/0` is missing, existing v6.4 behavior remains.

## Install

```bash
cd ~/Photonics/klayout-photonics-pdk
unzip -o ~/Downloads/klayout_phase3e61_obstacle_layer.zip -d .
python3 -m py_compile photonics/integration/router_v64.py
klayout -b -r tests/test_router_v64_klayout.py
klayout -b -r tests/test_router_v64_obstacle_layer.py
cp pymacros/photonics_router_v6_4.lym ~/.klayout/pymacros/
```

Restart KLayout and reopen `tests/phase3e5_output/waypoint_detour.gds` to test the GUI. The old straight-through route already present in the GDS is on `1/0`; the GUI router will treat it as an existing obstacle, and may refuse to route. For a clean visual demonstration, start with only the 90/0 obstacle and two unconnected port PCells, rather than a previously routed GDS.

The generated `1/0` polygon may not be recognized by older path-only photonic netlist extraction. This remains outside this patch's scope. Run the KLayout tests on the user's machine; the package has been syntax-checked but not executed against KLayout here.
