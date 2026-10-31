# Phase 3A — Router v6.1 extraction adapter

Overlay this archive at the repository root. It adds only `photonics/integration/` and `tests/test_router_adapter.py`; no existing files are overwritten.

```bash
python3 -m unittest discover -s tests -p 'test_router_adapter.py' -v
```

KLayout Python console usage (ensure the repository root is on `sys.path`):

```python
from photonics.integration import from_router_v61
ports, devices, nets = extract_photonic_netlist(cell, layout)
circuit = from_router_v61(ports, devices, nets, name=cell.name)
print(circuit.to_dict())
```

The last snippet requires `extract_photonic_netlist`, `cell`, and `layout` to be defined in the running KLayout context. This package does not yet integrate the GUI plugin. v6.1 can extract overlapping nets sharing a port; conversion raises ValueError in that case rather than dropping connections.
