# Phase 2: Circuit Model (standalone prototype)

Adds a pya-free circuit model preserving v6.1 class constructor signatures and core attributes.

## Install
From the repository root, unzip the archive. It adds files under `photonics/circuit/` and `tests/` only. Existing `.lym` files are not modified.

## Test
`python3 -m unittest discover -s tests -p 'test_circuit_model.py' -v`

## Compatibility boundary
This is a standalone model, **not yet integrated with the Router**. `PhotonicCircuit.from_extraction()` accepts the triple returned by v6.1, but the old classes are still distinct Python classes. A future adapter will bridge them. `PhotonicNet` rejects double attachment of a port (stricter than v6.1). `Point` is a pya-free convenience type; existing `pya.DPoint` objects are also accepted as port positions.

## Next
Add an adapter and KLayout batch integration tests before changing the Router macro.
