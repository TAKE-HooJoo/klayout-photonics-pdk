"""Symmetric Euler (clothoid) bend geometry, independent of KLayout.

Coordinates are in micrometres. A linearly increasing then decreasing
curvature profile produces a G2 transition to straight waveguides.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class EulerPoint:
    s: float
    x: float
    y: float
    theta: float
    curvature: float


def symmetric_euler_bend(angle_deg=90.0, min_radius_um=5.0,
                         samples=401, start=(0.0, 0.0), heading_deg=0.0):
    """Return sampled Euler bend with 0 -> peak -> 0 curvature.

    `min_radius_um` is the minimum *continuous-curve* radius. The bend
    angle must be in (-180, 180) degrees excluding zero. Sampling is
    uniform in arc length and includes the endpoints. A trapezoidal
    integration of heading gives accurate geometry without dependencies.
    """
    if not (math.isfinite(angle_deg) and 0 < abs(angle_deg) < 180):
        raise ValueError('angle_deg must be nonzero and within (-180,180)')
    if not (math.isfinite(min_radius_um) and min_radius_um > 0):
        raise ValueError('min_radius_um must be positive and finite')
    if not isinstance(samples, int) or samples < 3:
        raise ValueError('samples must be an integer >= 3')
    if not all(math.isfinite(float(v)) for v in (*start, heading_deg)):
        raise ValueError('start and heading must be finite')

    angle = math.radians(angle_deg)
    sign = 1.0 if angle > 0 else -1.0
    peak = sign / min_radius_um
    total_length = 2.0 * abs(angle) * min_radius_um
    half = total_length / 2.0
    initial = math.radians(heading_deg)

    def curvature(s):
        return peak * (s / half if s <= half else (total_length - s) / half)

    def theta(s):
        if s <= half:
            delta = peak * s * s / (2.0 * half)
        else:
            t = s - half
            delta = peak * (half / 2.0 + t - t*t/(2.0*half))
        return initial + delta

    step = total_length / (samples - 1)
    x, y = map(float, start)
    result = []
    for i in range(samples):
        s = total_length * i / (samples - 1)
        result.append(EulerPoint(s, x, y, theta(s), curvature(s)))
        if i < samples - 1:
            # Simpson integration of the unit tangent on each interval.
            a = theta(s)
            m = theta(s + step/2)
            b = theta(s + step)
            x += step * (math.cos(a) + 4*math.cos(m) + math.cos(b)) / 6
            y += step * (math.sin(a) + 4*math.sin(m) + math.sin(b)) / 6
    return tuple(result)
