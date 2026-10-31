# Phase 3E-7.6E — Hybrid Router v6.5 GUI

This package creates `pymacros/photonics_router_v6_5.lym` **from your actual existing** `pymacros/photonics_router_v6_4.lym`. The v6.4 file is not modified. The new GUI retains native port discovery, two-click operation, and v6.4's existing helpers, but invokes the tested `route_between_ports_hybrid` integration API.

## Install / build

From the repository root:

```bash
unzip -o ~/Downloads/klayout_phase3e76e_gui.zip
python3 tools/build_router_v65_gui.py
python3 -m unittest discover -s tests -p 'test_router_v65_gui_build.py' -v
```

Then copy the generated macro to KLayout's user macros directory and restart KLayout:

```bash
cp pymacros/photonics_router_v6_5.lym ~/.klayout/pymacros/
```

Three separate KLayout plugin tools are registered, named **Photonics Router v6.5 AUTO**, **CSC**, and **EULER**. Select the desired tool, then click source and destination optical ports. This avoids relying on version-dependent Qt modal dialogs and makes the selected mode explicit. Keep the existing v6.4 tool available for regression comparisons.

The v6.5 GUI uses the same PDK rules as the v6.4 GUI, including `MIN_BEND_RADIUS = 5.0` in the supplied macro. This is a prototype rule, not a foundry DRC signoff. The hybrid integration module inserts geometry only after route validation succeeds.

## Validation

The provided test verifies macro XML, Python syntax, three registered modes, integration call, and that the source v6.4 macro remains unchanged. **Actual KLayout GUI click interaction must be verified manually**; the test does not simulate mouse clicks. Verify EULER, CSC, AUTO, and rejected keepout scenarios. Confirm that an invalid route does not create shapes.

## Git

```bash
git add tools/build_router_v65_gui.py tests/test_router_v65_gui_build.py README_PHASE3E76E.md pymacros/photonics_router_v6_5.lym
git diff --cached --check
git commit -m 'Add Phase 3E-7.6E hybrid router v6.5 GUI modes'
git push origin main
```
