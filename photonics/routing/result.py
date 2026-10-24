from dataclasses import dataclass
from typing import Optional, Tuple
from photonics.circuit.geometry import Point

@dataclass(frozen=True)
class RouteResult:
    points: Tuple[Point, ...]
    length_um: float
    designed_radius_um: float
    measured_radius_um: float
    tangent_error_source_deg: float
    tangent_error_destination_deg: float
    valid: bool
    variant: str
    reason: str = ''
