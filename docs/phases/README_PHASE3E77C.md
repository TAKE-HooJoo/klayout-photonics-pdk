# Phase 3E-7.7C — Euler S-Bend integration in v6.5 Hybrid Router

This patch updates **only** `photonics/integration/router_hybrid_v65.py`.

- AUTO candidate order: `SBEND -> EULER -> CSC`
- EULER candidate order: `SBEND -> EULER`
- CSC: unchanged
- Validates candidate via existing endpoint, sharp-corner, sampled-radius, designed-radius, tangent and clearance checks before final insertion.
- S-Bend uses destination **arrival travel heading**, opposite the destination outward port vector.
- Returns `variant='EULER_SBEND'` for successful S-Bend.

## Apply

From repo root:

```bash
python3 apply_phase3e77c.py
python3 -m unittest discover -s tests -p 'test_euler_sbend.py' -v
klayout -b -r tests/test_euler_sbend_klayout.py
klayout -b -r tests/test_router_hybrid_v65_klayout.py
```

The last command assumes the existing v6.5 test filename; check with `ls tests/*hybrid*` if different.

A backup `router_hybrid_v65.py.phase3e77c.bak` is created. It should not be committed.

## Additional manual GUI check

Restart KLayout; use AUTO on two parallel-heading ports. Expect `EULER_SBEND` if geometrically feasible and clearance-valid; otherwise existing CSC fallback. Test perpendicular ports for Euler 90° and blocked routes for no insertion.

**Note:** this patch does not modify the GUI's display logic. If the GUI assumes only `EULER` or CSC variants, the status display may need a separate update. Sampled radius is not foundry DRC signoff.
