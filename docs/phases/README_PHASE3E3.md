# Phase 3E-3: CSC obstacle-aware route selection

This package adds a **non-mutating** KLayout adapter. It enumerates CSC candidates and tests each route's physical waveguide polygon against a supplied obstacle `pya.Region` using the existing Phase 3E-2 clearance checker. It does not modify v6.3 or insert a path.

## Install

From `~/Photonics/klayout-photonics-pdk`:

```bash
unzip -n ~/Downloads/klayout_phase3e3_obstacle_router.zip -d .
klayout -b -r tests/test_klayout_obstacle_router.py
```

## Limitations

- Intended endpoint-device geometries **must be explicitly excluded or locally clipped** before calling; no automatic exemptions are made.
- Only straight and the existing four CSC candidates are considered. No waypoint/CSCSC fallback.
- The existing engine's arc-turn and detour length limits remain in force.
- `Region.sized()` is a conservative DBU-grid clearance screen, not a sign-off DRC.
- Test with the target KLayout build; this ZIP has not been KLayout-runtime verified in the user's environment.
