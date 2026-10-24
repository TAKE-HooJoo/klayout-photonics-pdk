from dataclasses import dataclass
import math

@dataclass(frozen=True)
class WaveguideCrossSection:
    name: str
    width_um: float
    min_bend_radius_um: float
    layer: str = 'waveguide'

    def __post_init__(self):
        if not self.name.strip() or not self.layer.strip():
            raise ValueError('Name and layer are required')
        for value in (self.width_um, self.min_bend_radius_um):
            if not math.isfinite(value) or value <= 0:
                raise ValueError('Dimensions must be finite and positive')
