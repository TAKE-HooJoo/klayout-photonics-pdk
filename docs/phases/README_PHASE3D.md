# Phase 3D: KLayout interactive Router v6.3 (experimental)

This package **does not modify v6.2**. It generates a new `pymacros/photonics_router_v6_3.lym` from your existing `refined_cscsc` macro, retaining its PCell port discovery, but replacing the GUI's routing call with the independent `photonics.integration.router_v62.route_between_ports`.

## Install / build

From your repository root:

```bash
unzip -o klayout_pdk_phase3d.zip
python3 tools/build_router_v63.py --root "$PWD"
python3 -m unittest discover -s tests -p 'test_router_v63_macro.py' -v
python3 -m unittest discover -s tests -p 'test_routing_engine.py' -v
klayout -b -r tests/test_klayout_routing.py
```

Then install v6.3 as an **additional** macro (do not replace v6.2):

```bash
cp pymacros/photonics_router_v6_3.lym ~/.klayout/pymacros/
```

Restart KLayout and select **Photonics Router v6.3**, then click source and destination optical ports. The macro imports the `photonics` Python package from the checkout path embedded at generation time.

## Known limitations

- The independent Phase 3C engine supports **straight and single CSC Dubins routes only**, not the legacy refined v6.2 CSCSC fallback. Some port arrangements that v6.2 could route may report `NO_LEGAL_CSC_ROUTE`.
- The `0.4 um` minimum width and `0.5 um` spacing are **prototype** design-rule values, not a foundry-qualified PDK. Radius is inherited from v6.2's prototype `MIN_BEND_RADIUS`.
- Radius from sampled points is diagnostic, not a foundry DRC certification.
- GUI clicking must be tested manually in KLayout; static and batch tests do not verify plugin activation or mouse interaction.
- This first GUI bridge uses legacy port discovery; a future iteration should use a dedicated port adapter and configuration object.
