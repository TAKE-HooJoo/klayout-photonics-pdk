"""KLayout batch smoke test. Run from repository root using klayout -b -r."""
import os
import sys
import json
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.getcwd())
sys.path.insert(0, ROOT)
import pya
from photonics.integration.router_v61 import from_router_v61


def macro_python(path):
    root = ET.parse(path).getroot()
    code = root.findtext('text')
    if not code:
        raise RuntimeError('Macro has no Python text: ' + path)
    return code


def main():
    pdk_path = os.path.join(ROOT, 'pymacros', 'photonics_pdk_v4.lym')
    router_path = os.path.join(ROOT, 'pymacros', 'photonics_router_v6_1.lym')
    # Execute library registration; no changes to original macro.
    exec(compile(macro_python(pdk_path), pdk_path, 'exec'), {'__name__': 'phase3b_pdk'})
    lib = pya.Library.library_by_name('Photonics')
    assert lib is not None, 'Photonics library missing'
    decl = lib.layout().pcell_declaration('Straight')
    assert decl is not None, 'Straight PCell missing'
    layout = pya.Layout()
    layout.dbu = 0.001
    top = layout.create_cell('PHASE3B_TOP')
    variants = []
    for length in (10.0, 10.0):
        idx = layout.add_pcell_variant(lib, decl.id(), {'length': length, 'width': 0.5})
        variants.append(idx)
    # A: x=0..10, B: x=30..40, connecting segment 10..30
    top.insert(pya.DCellInstArray(variants[0], pya.DTrans(0, False, 0, 0)))
    top.insert(pya.DCellInstArray(variants[1], pya.DTrans(0, False, 30, 0)))
    top.shapes(layout.layer(pya.LayerInfo(1, 0))).insert(
        pya.DPath([pya.DPoint(10, 0), pya.DPoint(30, 0)], 0.5))

    # Router's GUI plugin registration is deliberately excluded in batch mode.
    router_code = macro_python(router_path)
    marker = '\nclass Router(pya.Plugin):'
    assert marker in router_code, 'Router class boundary not found'
    router_ns = {'__name__': 'phase3b_router'}
    exec(compile(router_code.split(marker)[0], router_path, 'exec'), router_ns)
    ports, devices, nets = router_ns['extract_photonic_netlist'](top, layout)
    circuit = from_router_v61(ports, devices, nets, name='phase3b')
    print('Devices:', len(circuit.devices), 'Ports:', len(circuit.ports),
          'Nets:', len(circuit.nets), 'Unconnected:', len(circuit.unconnected_ports()))
    for port in circuit.ports:
        print('PORT', port.qualified_name, port.position.x, port.position.y)
    for net in circuit.nets:
        print('NET', net.name, [p.qualified_name for p in net.ports], net.length)
    assert len(circuit.devices) == 2, 'expected 2 devices'
    assert len(circuit.ports) == 4, 'expected 4 ports'
    assert len(circuit.nets) == 1, 'expected 1 net'
    assert len(circuit.unconnected_ports()) == 2, 'expected 2 unconnected ports'
    assert abs(circuit.nets[0].length - 20.0) < 0.01, 'unexpected routed length'
    out = os.path.join(ROOT, 'tests', 'phase3b_output')
    os.makedirs(out, exist_ok=True)
    layout.write(os.path.join(out, 'phase3b_two_straights.gds'))
    with open(os.path.join(out, 'phase3b_netlist.json'), 'w', encoding='utf-8') as f:
        json.dump(circuit.to_dict(), f, indent=2, ensure_ascii=False)
    print('Phase 3B: PASS')


if __name__ == '__main__':
    main()
