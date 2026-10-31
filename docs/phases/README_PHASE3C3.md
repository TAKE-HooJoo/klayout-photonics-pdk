# Phase 3C-3: KLayout batch integration

Prerequisites: Phase 1–3C-2 files already installed, including `photonics/routing/`.

Unzip at the repository root. Then run:

```bash
python3 -m unittest discover -s tests -p 'test_routing_engine.py' -v
klayout -b -r tests/test_klayout_integration.py
klayout -b -r tests/test_klayout_routing.py
```

The last test creates `tests/phase3c3_output/phase3c3_s_bend.gds` and a netlist JSON. Do not commit generated outputs unless desired.

This adapter uses the v6.1 extractor to verify the route and does not alter the v6.2 GUI macro. The route engine currently supports straight and CSC paths, **not** waypoint CSCSC; `NO_LEGAL_CSC_ROUTE` is a legitimate failure. Designed radius is not a manufacturing DRC certification; the sampled radius is diagnostic. If the netlist extractor fails to recognize the new path, investigate port orientations and extraction tolerances before modifying existing code.
