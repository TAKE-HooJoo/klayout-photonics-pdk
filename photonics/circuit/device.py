class PhotonicDevice:
    def __init__(self, name, cell_name):
        self.name = name
        self.cell_name = cell_name
        self.ports = []

    def add_port(self, port):
        if port.device is not None and port.device is not self:
            raise ValueError("port belongs to another device")
        if port not in self.ports:
            self.ports.append(port)
        port.device = self

    def __repr__(self):
        return "PhotonicDevice(%s, type=%s, ports=%d)" % (
            self.name, self.cell_name, len(self.ports))
