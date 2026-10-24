from dataclasses import dataclass, field

@dataclass(frozen=True)
class LayerSpec:
    layer: int
    datatype: int = 0

    def __post_init__(self):
        if self.layer < 0 or self.datatype < 0:
            raise ValueError('Layer and datatype must be nonnegative')

@dataclass(frozen=True)
class LayerMap:
    waveguide: LayerSpec = field(default_factory=lambda: LayerSpec(1, 0))
    optical_pin: LayerSpec = field(default_factory=lambda: LayerSpec(2, 0))
