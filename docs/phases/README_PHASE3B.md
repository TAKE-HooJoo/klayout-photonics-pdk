# Phase 3B: KLayout batch integration smoke test

Run from the repository root after Phase 1, 2, and 3A have been installed:

```bash
unzip ~/Downloads/klayout_pdk_phase3b.zip -d .
klayout -b -r tests/test_klayout_integration.py
```

Expected: 2 devices, 4 ports, 1 net, 2 unconnected ports, 20 um routed segment. Outputs under `tests/phase3b_output/`.

The test executes the PCell macro's Python body to register the library and executes only the Router v6.1 data-extraction functions, avoiding GUI plugin registration. It does not modify existing macros. KLayout 0.30.9 runtime execution has **not** been verified here; share the traceback if an API mismatch occurs.

Note: net length is only the 20 um inter-device routing segment, not the internal lengths of both Straight PCells.
