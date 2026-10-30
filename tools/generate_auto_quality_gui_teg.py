"""Generate a *port-bearing PCell* GUI routing TEG in KLayout.

Run with: klayout -b -r tools/generate_auto_quality_gui_teg.py
The photonics PCell library must be registered in this KLayout installation.
No routing is drawn; this is an input for GUI routing tests.
"""
import os
import sys
import pya

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

OUT = os.path.join(ROOT, 'tests', 'phase3e78c3_gui_teg')
DBU = 0.001
WG = pya.LayerInfo(1, 0)
PIN = pya.LayerInfo(2, 0)


def find_straight():
    found = []
    for name in pya.Library.library_names():
        lib = pya.Library.library_by_name(name)
        if lib is None:
            continue
        decl = lib.layout().pcell_declaration('Straight')
        if decl is not None:
            found.append((name, lib, decl))
    if not found:
        raise RuntimeError('No registered Straight PCell. Load the Photonics PDK PCell macro in KLayout first.')
    # Favor the photonics library if more than one library defines Straight.
    found.sort(key=lambda item: (not ('photon' in item[0].lower()), item[0]))
    return found[0]


def default_params(decl):
    result = {}
    for p in decl.get_parameters():
        # KLayout PCellParameterDeclaration exposes name and default.
        result[p.name] = p.default
    return result


def shape_count(cell, layer_index):
    return sum(1 for _ in cell.begin_shapes_rec(layer_index))


def main():
    name, lib, decl = find_straight()
    layout = pya.Layout()
    layout.dbu = DBU
    top = layout.create_cell('AUTO_QUALITY_GUI_TEG')
    params = default_params(decl)
    # Explicitly keep the device defaults. Avoid guessing PCell parameter names.
    idx = layout.add_pcell_variant(lib, decl.id(), params)
    if idx is None or idx < 0:
        raise RuntimeError('Could not create Straight PCell variant')
    # A right-facing Straight and an opposing Straight, offset in Y.
    # The two-click GUI router should use the facing optical ports.
    placements = [
        pya.Trans(pya.Trans.R0, 0, 0),
        pya.Trans(pya.Trans.R180, int(round(300 / DBU)), int(round(40 / DBU))),
    ]
    for tr in placements:
        top.insert(pya.CellInstArray(idx, tr))
    pin_index = layout.find_layer(PIN)
    pin_count = shape_count(top, pin_index) if pin_index is not None and pin_index >= 0 else 0
    if pin_count < 4:
        raise RuntimeError('Expected >=4 optical pin shapes on 2/0, got %d. '
                           'Check PCell optical-port settings and layer mapping.' % pin_count)
    wg_index = layout.find_layer(WG)
    wg_count = shape_count(top, wg_index) if wg_index is not None and wg_index >= 0 else 0
    if wg_count < 2:
        raise RuntimeError('Expected >=2 waveguide shapes on 1/0, got %d' % wg_count)
    os.makedirs(OUT, exist_ok=True)
    gds = os.path.join(OUT, 'auto_quality_unrouted_ports.gds')
    oas = os.path.join(OUT, 'auto_quality_unrouted_ports.oas')
    layout.write(gds)
    layout.write(oas)
    print('Library:', name)
    print('PCell: Straight, parameters:', params)
    print('Optical pin shapes (recursive):', pin_count)
    print('Waveguide shapes (recursive):', wg_count)
    print('GDS:', gds)
    print('OAS:', oas)
    print('Phase 3E-7.8C-3 GUI TEG generation: PASS')
    print('NOTE: GDS/OAS may not preserve live PCell metadata; confirm GUI port detection after opening.')


if __name__ == '__main__':
    main()
