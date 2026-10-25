"""Polyline turn diagnostics. Coordinates are micrometres."""
import math
from photonics.routing.geometry import length


def turn_angles_deg(points):
    """Unsigned direction change at each interior vertex (degrees)."""
    result = []
    for a, b, c in zip(points, points[1:], points[2:]):
        ux, uy = b.x-a.x, b.y-a.y
        vx, vy = c.x-b.x, c.y-b.y
        nu, nv = math.hypot(ux, uy), math.hypot(vx, vy)
        if min(nu, nv) <= 1e-12:
            raise ValueError('Degenerate segment')
        result.append(math.degrees(math.atan2(abs(ux*vy-uy*vx), ux*vx+uy*vy)))
    return tuple(result)


def sharp_corners(points, threshold_deg=5.0):
    if not math.isfinite(threshold_deg) or not 0 < threshold_deg < 180:
        raise ValueError('Invalid threshold')
    return tuple((i+1, angle) for i, angle in enumerate(turn_angles_deg(points))
                 if angle > threshold_deg)
