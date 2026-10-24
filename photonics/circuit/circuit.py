class PhotonicCircuit:
    def __init__(self, name="circuit"):
        self.name = name
        self.devices = {}
        self.nets = []
        self.ports = []

    def add_device(self, device):
        if device.name in self.devices and self.devices[device.name] is not device:
            raise ValueError("duplicate device name: %s" % device.name)
        self.devices[device.name] = device
        for port in device.ports:
            self.add_port(port)
        return device

    def add_port(self, port):
        if port not in self.ports:
            self.ports.append(port)
        return port

    def add_net(self, net):
        if any(existing.name == net.name and existing is not net for existing in self.nets):
            raise ValueError("duplicate net name: %s" % net.name)
        if net not in self.nets:
            self.nets.append(net)
        for port in net.ports:
            self.add_port(port)
        return net

    @classmethod
    def from_extraction(cls, ports, devices, nets, name="circuit"):
        circuit = cls(name)
        for port in ports:
            circuit.add_port(port)
        for device in devices.values() if isinstance(devices, dict) else devices:
            circuit.add_device(device)
        for net in nets:
            circuit.add_net(net)
        return circuit

    def unconnected_ports(self):
        return [p for p in self.ports if p.net is None]

    def to_dict(self):
        return {
            "name": self.name,
            "devices": [{"name": d.name, "cell_name": d.cell_name,
                         "ports": [p.qualified_name for p in d.ports]}
                        for d in self.devices.values()],
            "nets": [{"name": n.name, "ports": [p.qualified_name for p in n.ports],
                      "length_um": n.length} for n in self.nets],
            "unconnected_ports": [p.qualified_name for p in self.unconnected_ports()],
        }
