"""Convert Router v6.1 extraction objects into the independent Circuit Model.

No import of pya: accepts (ports, devices, nets) from extract_photonic_netlist().
The v6.1 extractor may assign a port to multiple nets; this adapter rejects
such cases explicitly rather than silently losing connectivity.
"""
from photonics.circuit import Point, OpticalPort, PhotonicDevice, PhotonicNet, PhotonicCircuit


def from_router_v61(ports, devices, nets, name="circuit"):
    circuit = PhotonicCircuit(name)
    mapped = {}
    for old in ports:
        if id(old) in mapped:
            raise ValueError("duplicate source port object")
        p = OpticalPort(old.name, Point(float(old.position.x), float(old.position.y)),
                        old.direction, float(old.width), old.instance_name, old.cell_name)
        mapped[id(old)] = p
        circuit.add_port(p)
    device_values = devices.values() if isinstance(devices, dict) else devices
    for old_device in device_values:
        d = PhotonicDevice(old_device.name, old_device.cell_name)
        for old_port in old_device.ports:
            if id(old_port) not in mapped:
                raise ValueError("device references an unknown port")
            d.add_port(mapped[id(old_port)])
        circuit.add_device(d)
    for old_net in nets:
        new_ports = []
        for old_port in old_net.ports:
            if id(old_port) not in mapped:
                raise ValueError("net references an unknown port")
            new_ports.append(mapped[id(old_port)])
        circuit.add_net(PhotonicNet(old_net.name, new_ports, float(old_net.length)))
    return circuit
