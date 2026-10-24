class OpticalPort:
    """pya-free optical port; position accepts any object with x and y."""
    def __init__(self, name, position, direction, width=0.5,
                 instance_name=None, cell_name=None):
        if width <= 0:
            raise ValueError("port width must be positive")
        self.name = name
        self.position = position
        self.direction = direction
        self.width = width
        self.instance_name = instance_name
        self.cell_name = cell_name
        self.device = None
        self.net = None

    @property
    def qualified_name(self):
        if self.device is not None:
            return "%s.%s" % (self.device.name, self.name)
        if self.instance_name:
            return "%s.%s" % (self.instance_name, self.name)
        return self.name

    def __repr__(self):
        return "OpticalPort(%s, x=%.3f, y=%.3f, width=%.3f)" % (
            self.qualified_name, self.position.x, self.position.y, self.width)
