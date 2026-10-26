"""Endpoint-constrained Straight–Euler–Straight routing for +/-90 degree turns.

Pure Python, no KLayout dependency. All positions and lengths are in um.
Only a single monotone quarter-turn is supported. Infeasible requests fail closed.
"""
from dataclasses import dataclass
import math
from photonics.routing.euler_bend import symmetric_euler_bend


@dataclass(frozen=True)
class EulerRouteResult:
    valid: bool
    reason: str
    points: tuple
    source_lead_um: float
    destination_lead_um: float
    min_radius_um: float
    length_um: float
    endpoint_error_um: float
    heading_error_deg: float


def route_straight_euler_straight(source, destination, source_heading_deg,
                                  destination_heading_deg, min_radius_um=6.25,
                                  samples=401, position_tolerance_um=0.01,
                                  heading_tolerance_deg=0.1):
    """Solve two nonnegative straight leads around a symmetric Euler quarter-turn.

    Geometry is source -> straight along source heading -> Euler -> straight
    along destination heading -> destination. Curvature is continuous at joins.
    The Euler uses the minimum permitted radius; no smaller-radius fallback.
    Returns an invalid result when the fixed geometry cannot fit.
    """
    values = (*source, *destination, source_heading_deg, destination_heading_deg,
              min_radius_um, position_tolerance_um, heading_tolerance_deg)
    if len(source) != 2 or len(destination) != 2 or not all(math.isfinite(float(v)) for v in values):
        raise ValueError('Coordinates and parameters must be finite')
    if min_radius_um <= 0 or position_tolerance_um <= 0 or heading_tolerance_deg <= 0:
        raise ValueError('Radius and tolerances must be positive')
    if not isinstance(samples, int) or samples < 3:
        raise ValueError('samples must be >= 3')

    turn = (destination_heading_deg - source_heading_deg + 180.0) % 360.0 - 180.0
    if abs(abs(turn) - 90.0) > heading_tolerance_deg:
        return EulerRouteResult(False, 'UNSUPPORTED_TURN_ANGLE', (), 0, 0,
                                min_radius_um, 0, math.inf, abs(abs(turn) - 90))
    turn = 90.0 if turn > 0 else -90.0
    bend = symmetric_euler_bend(turn, min_radius_um, samples=samples)
    theta = math.radians(source_heading_deg)
    c, s = math.cos(theta), math.sin(theta)
    dx, dy = destination[0]-source[0], destination[1]-source[1]
    # Transform target into source-heading coordinates.
    tx, ty = c*dx+s*dy, -s*dx+c*dy
    bx, by = bend[-1].x, bend[-1].y
    sign = 1 if turn > 0 else -1
    lead1, lead2 = tx-bx, sign*(ty-by)
    if lead1 < -position_tolerance_um or lead2 < -position_tolerance_um:
        return EulerRouteResult(False, 'INSUFFICIENT_LEAD_SPACE', (),
                                max(0, lead1), max(0, lead2), min_radius_um,
                                0, math.inf, 0)
    lead1, lead2 = max(0.0, lead1), max(0.0, lead2)

    def global_point(x, y):
        return (source[0]+c*x-s*y, source[1]+s*x+c*y)

    p0 = (float(source[0]), float(source[1]))
    p1 = global_point(lead1, 0)
    middle = tuple(global_point(lead1+p.x, p.y) for p in bend)
    end = global_point(lead1+bx, by+sign*lead2)
    points = (p0, p1) + middle + (end,)
    # Remove duplicate joins while retaining the exact endpoint coordinates.
    dedup = [points[0]]
    for p in points[1:]:
        if math.hypot(p[0]-dedup[-1][0], p[1]-dedup[-1][1]) > 1e-12:
            dedup.append(p)
    error = math.hypot(end[0]-destination[0], end[1]-destination[1])
    heading_error = abs((source_heading_deg+turn-destination_heading_deg+180)%360-180)
    valid = error <= position_tolerance_um and heading_error <= heading_tolerance_deg
    return EulerRouteResult(valid, '' if valid else 'ENDPOINT_MISMATCH',
                            tuple(dedup) if valid else (), lead1, lead2,
                            min_radius_um, bend[-1].s+lead1+lead2,
                            error, heading_error)
