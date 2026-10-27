"""Phase 3E-7.7A: parallel-heading Euler S-bend, pure Python.

Connect ports with equal travel heading using two opposite symmetric Euler
turns and optional straight leads. Units: um, degrees. Fail closed.
"""
from dataclasses import dataclass
import math
from photonics.routing.euler_bend import symmetric_euler_bend


@dataclass(frozen=True)
class EulerSBendResult:
    valid: bool
    reason: str
    points: tuple
    length_um: float
    min_radius_um: float
    bend_angle_deg: float
    lead_um: float
    endpoint_error_um: float
    heading_error_deg: float


def _failure(reason, radius):
    return EulerSBendResult(False, reason, (), 0.0, radius, 0.0, 0.0, math.inf, math.inf)


def route_euler_sbend(source, destination, source_heading_deg,
                      destination_heading_deg, min_radius_um=6.25,
                      samples_per_bend=201, position_tolerance_um=0.01,
                      heading_tolerance_deg=0.1, max_turn_deg=89.0):
    """Construct +theta/-theta (or reversed) Euler turns with straight leads.

    Supported: parallel travel headings, forward displacement, nonzero lateral
    offset. Zero offset yields a straight line. Does not check obstacles or
    waveguide width; the integration layer must validate those before placement.
    """
    if len(source) != 2 or len(destination) != 2:
        raise ValueError('source/destination must be 2D')
    vals = (*source, *destination, source_heading_deg, destination_heading_deg,
            min_radius_um, position_tolerance_um, heading_tolerance_deg, max_turn_deg)
    if not all(math.isfinite(float(v)) for v in vals):
        raise ValueError('all values must be finite')
    if min_radius_um <= 0 or position_tolerance_um <= 0 or heading_tolerance_deg <= 0:
        raise ValueError('radius/tolerances must be positive')
    if not isinstance(samples_per_bend, int) or samples_per_bend < 5:
        raise ValueError('samples_per_bend must be >= 5')
    if not 0 < max_turn_deg < 90:
        raise ValueError('max_turn_deg must be between 0 and 90')
    delta = (destination_heading_deg-source_heading_deg+180) % 360-180
    if abs(delta) > heading_tolerance_deg:
        return _failure('UNSUPPORTED_HEADING_DIFFERENCE', min_radius_um)
    heading = math.radians(source_heading_deg)
    c, s = math.cos(heading), math.sin(heading)
    dx, dy = destination[0]-source[0], destination[1]-source[1]
    forward, lateral = c*dx+s*dy, -s*dx+c*dy
    if forward < -position_tolerance_um:
        return _failure('DESTINATION_BEHIND_SOURCE', min_radius_um)
    if abs(lateral) <= position_tolerance_um:
        if forward <= position_tolerance_um:
            return _failure('COINCIDENT_PORTS', min_radius_um)
        return EulerSBendResult(True, '', (tuple(map(float, source)), tuple(map(float, destination))),
                                forward, math.inf, 0.0, forward, 0.0, abs(delta))
    sign = 1.0 if lateral > 0 else -1.0
    target_y = abs(lateral)

    def pair(theta):
        # First Euler: heading 0 -> +theta; second is its time-reversed
        # mirror, heading +theta -> 0. Transform second samples by reflecting
        # the first curve about its endpoint tangent.
        bend = symmetric_euler_bend(math.degrees(theta), min_radius_um,
                                    samples=samples_per_bend)
        bx, by = bend[-1].x, bend[-1].y
        # second turn local delta = rotation(theta) * mirror_y(first bend)
        x2 = math.cos(theta)*bx + math.sin(theta)*by
        y2 = math.sin(theta)*bx - math.cos(theta)*by
        return bend, bx+x2, by+y2

    lo, hi = 0.0, math.radians(max_turn_deg)
    _, _, max_y = pair(hi)
    if target_y > max_y + position_tolerance_um:
        return _failure('LATERAL_OFFSET_TOO_LARGE', min_radius_um)
    for _ in range(65):
        mid = (lo+hi)/2
        _, _, ym = pair(mid)
        if ym < target_y:
            lo = mid
        else:
            hi = mid
    theta = (lo+hi)/2
    bend, bend_x, bend_y = pair(theta)
    lead_total = forward-bend_x
    if lead_total < -position_tolerance_um:
        return _failure('INSUFFICIENT_FORWARD_SPACE', min_radius_um)
    lead_total = max(0.0, lead_total)
    lead_a = lead_total/2
    lead_b = lead_total-lead_a
    bx, by = bend[-1].x, bend[-1].y
    ct, st = math.cos(theta), math.sin(theta)
    local = [(0.0, 0.0)]
    if lead_a > 1e-12:
        local.append((lead_a, 0.0))
    local.extend((lead_a+p.x, p.y) for p in bend[1:])
    for p in bend[1:]:
        x2 = ct*p.x+st*p.y
        y2 = st*p.x-ct*p.y
        local.append((lead_a+bx+x2, by+y2))
    if lead_b > 1e-12:
        local.append((forward, bend_y))
    if sign < 0:
        local = [(x, -y) for x, y in local]
    points = tuple((float(source[0])+c*x-s*y,
                    float(source[1])+s*x+c*y) for x, y in local)
    endpoint_error = math.dist(points[-1], destination)
    if endpoint_error > position_tolerance_um:
        return _failure('ENDPOINT_MISMATCH', min_radius_um)
    # Analytic length from Euler samples, not polyline chord sum.
    route_length = 2*bend[-1].s+lead_total
    return EulerSBendResult(True, '', points, route_length, min_radius_um,
                            math.degrees(theta), lead_total, endpoint_error,
                            abs(delta))
