# Phase 1: PDK Model

Pure Python prototype, independent of KLayout `pya`.

## Install into existing repository

Copy `photonics/` and `tests/test_pdk_model.py` to the repository root.
Existing PCells and routers are not modified.

## Test

```bash
python3 -m unittest discover -s tests -p 'test_pdk_model.py' -v
```

## Notes

The test values (0.4 um minimum width, 0.2 um spacing, 5 um radius) are illustrative and are NOT foundry-qualified design rules.
`validate_cross_section` checks only width and minimum radius; spacing requires geometry-level verification in a later phase.
