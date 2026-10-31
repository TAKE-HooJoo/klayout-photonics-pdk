# Phase 3C-2: Independent CSC Routing Engine

This is an additive overlay for the existing klayout-photonics-pdk repository.
It leaves all existing macros and PDK/Circuit models untouched.

## Install
From repository root:

```bash
unzip -o klayout_pdk_phase3c2.zip
python3 -m unittest discover -s tests -p 'test_routing_engine.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The full test discovery may require KLayout for `test_klayout_integration.py`;
run that separately with `klayout -b -r tests/test_klayout_integration.py`.

## Scope
- Pure-Python CSC routing: LSL, RSR, LSR, RSL
- PDK cross-section/rules validation
- Strict outward port direction conventions
- Sampled minimum radius reported as diagnostic, not manufacturing DRC
- No CSCSC waypoint fallback yet
- No GUI/GDS integration yet

## Caveat
Circular arcs are sampled as a polyline for downstream DPath use.
A sampled circumcircle estimate near straight/arc joins is not a reliable
proof of minimum continuous curvature; the designed circular arc radius
is tracked separately. Exact centerline length is also not yet exported.
