class PhotonicNet:
    def __init__(self, name, ports, length=0.0):
        ports = list(ports)
        if length < 0:
            raise ValueError("net length must not be negative")
        if len({id(p) for p in ports}) != len(ports):
            raise ValueError("duplicate port in net")
        if any(p.net is not None for p in ports):
            raise ValueError("port already belongs to a net")
        self.name = name
        self.ports = ports
        self.length = length
        for port in ports:
            port.net = self

    def __repr__(self):
        return "PhotonicNet(%s, ports=%s, length=%.3f)" % (
            self.name, [p.qualified_name for p in self.ports], self.length)
