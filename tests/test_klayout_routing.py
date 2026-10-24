"""Run from repository root: klayout -b -r tests/test_klayout_routing.py"""
import json
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.getcwd())
sys.path.insert(0, ROOT)
import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.router_v61 import from_router_v61
from photonics.integration.router_v62 import route_between_ports


def macro_code(path):
    code = ET.parse(path).getroot().findtext('text')
    if not code:
        raise RuntimeError('No macro Python text: ' + path)
    return code


def main():
    pdk_file = os.path.join(ROOT, 'pymacros/photonics_pdk_v4.lym')
    router_file = os.path.join(ROOT, 'pymacros/photonics_router_v6_1.lym')
    exec(compile(macro_code(pdk_file), pdk_file, 'exec'), {'__name__': 'phase3c3_pdk'})
    lib = pya.Library.library_by_name('Photonics')
    assert lib is not None, 'Photonics library missing'
    decl = lib.layout().pcell_declaration('Straight')
    assert decl is not None, 'Straight PCell missing'

    layout = pya.Layout()
    layout.dbu = 0.001
    top = layout.create_cell('PHASE3C3_TOP')
    idx = layout.add_pcell_variant(lib, decl.id(), {'length': 10.0, 'width': 0.5})
    # First PCell: x=0..10, y=0; second: x=60..70, y=15.
    top.insert(pya.DCellInstArray(idx, pya.DTrans(0, False, 0, 0)))
    top.insert(pya.DCellInstArray(idx, pya.DTrans(0, False, 60, 15)))

    router_code = macro_code(router_file)
    boundary = '\nclass Router(pya.Plugin):'
    assert boundary in router_code
    namespace = {'__name__': 'phase3c3_router'}
    exec(compile(router_code.split(boundary)[0], router_file, 'exec'), namespace)
    ports_before = namespace['collect_ports'](top, layout)
    source = min(ports_before, key=lambda p: (p.position.x - 10)**2 + p.position.y**2)
    destination = min(ports_before, key=lambda p: (p.position.x - 60)**2 + (p.position.y - 15)**2)
    assert abs(source.position.x - 10) < 0.01
    assert abs(destination.position.x - 60) < 0.01

    xs = WaveguideCrossSection('strip', 0.5, 5.0)
    rules = DesignRules(0.4, 0.5, 5.0)
    result = route_between_ports(top, layout, source, destination, xs, rules)
    assert result.valid, 'Routing failed: ' + result.reason
    assert result.length_um > 0
    assert len(result.points) > 2, 'Expected curved route'
    assert max(result.tangent_error_source_deg,
               result.tangent_error_destination_deg) <= 5.0

    ports, devices, nets = namespace['extract_photonic_netlist'](top, layout)
    circuit = from_router_v61(ports, devices, nets, name='phase3c3')
    assert len(circuit.devices) == 2, len(circuit.devices)
    assert len(circuit.ports) == 4, len(circuit.ports)
    assert len(circuit.nets) == 1, len(circuit.nets)
    assert len(circuit.unconnected_ports()) == 2
    assert abs(circuit.nets[0].length - result.length_um) < 0.1, (
        circuit.nets[0].length, result.length_um)

    output = os.path.join(ROOT, 'tests', 'phase3c3_output')
    os.makedirs(output, exist_ok=True)
    gds = os.path.join(output, 'phase3c3_s_bend.gds')
    layout.write(gds)
    with open(os.path.join(output, 'phase3c3_netlist.json'), 'w', encoding='utf-8') as f:
        json.dump(circuit.to_dict(), f, ensure_ascii=False, indent=2)
    print('Variant:', result.variant)
    print('Length (um):', round(result.length_um, 3))
    print('Designed radius (um):', result.designed_radius_um)
    print('Sampled radius (um):', result.measured_radius_um)
    print('Devices:', len(circuit.devices), 'Ports:', len(circuit.ports),
          'Nets:', len(circuit.nets))
    print('GDS:', gds)
    print('Phase 3C-3: PASS')


if __name__ == '__main__':
    main()
