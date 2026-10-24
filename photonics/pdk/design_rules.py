from dataclasses import dataclass
import math

@dataclass(frozen=True)
class DesignRules:
    min_waveguide_width_um: float
    min_waveguide_spacing_um: float
    min_bend_radius_um: float

    def __post_init__(self):
        for value in (self.min_waveguide_width_um, self.min_waveguide_spacing_um, self.min_bend_radius_um):
            if not math.isfinite(value) or value <= 0:
                raise ValueError('Rules must be finite and positive')

    def validate_cross_section(self, xs):
        return (xs.width_um >= self.min_waveguide_width_um and
                xs.min_bend_radius_um >= self.min_bend_radius_um)
