"""Phase 3E-7.6C: fail-closed CSC / Euler / Auto route selection.

Pure Python. No changes to existing v6.4 router. CSC is supplied as a
callback, since its public signature must be verified in the actual repository.
Coordinates are in micrometers. The callback must return a candidate with
`points` and `valid` fields (object or mapping); optional `reason`.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class SelectedRoute:
    valid: bool
    mode: str
    points: tuple
    reason: str
    attempts: tuple


def _get(candidate, name, default=None):
    return candidate.get(name, default) if isinstance(candidate, dict) else getattr(candidate, name, default)


def _validate(candidate, source, destination, position_tolerance_um,
              clearance_check):
    if candidate is None or not _get(candidate, 'valid', False):
        return None, _get(candidate, 'reason', 'ROUTE_NOT_FOUND') if candidate is not None else 'ROUTE_NOT_FOUND'
    raw = _get(candidate, 'points', ())
    try:
        points = tuple((float(p[0]), float(p[1])) for p in raw)
    except (TypeError, ValueError, IndexError):
        return None, 'INVALID_POINTS'
    if len(points) < 2 or not all(math.isfinite(v) for p in points for v in p):
        return None, 'INVALID_POINTS'
    if math.dist(points[0], source) > position_tolerance_um or math.dist(points[-1], destination) > position_tolerance_um:
        return None, 'ENDPOINT_MISMATCH'
    if clearance_check is not None and not clearance_check(points):
        return None, 'OBSTACLE_COLLISION'
    return points, ''


def select_route(source, destination, source_heading_deg, destination_heading_deg,
                 mode='AUTO', csc_router=None, clearance_check=None,
                 min_radius_um=6.25, samples=401,
                 position_tolerance_um=0.01, heading_tolerance_deg=0.1):
    """Select a route. No layout placement or side effects.

    `csc_router` callback: f(source, destination, source_heading_deg,
    destination_heading_deg) -> candidate with valid, points, reason.
    `clearance_check`: f(points) -> bool; supply an actual DRC/geometry check
    before using candidates for placement. CSC callback must independently
    enforce its own radius/tangent rules until a shared validator is added.
    """
    mode = str(mode).upper()
    if mode not in ('CSC', 'EULER', 'AUTO'):
        raise ValueError('mode must be CSC, EULER, or AUTO')
    if position_tolerance_um <= 0 or min_radius_um <= 0 or heading_tolerance_deg <= 0:
        raise ValueError('radius and tolerances must be positive')
    source, destination = tuple(source), tuple(destination)
    if len(source) != 2 or len(destination) != 2:
        raise ValueError('source and destination must have two coordinates')
    attempts = []
    order = ('EULER', 'CSC') if mode == 'AUTO' else (mode,)
    for candidate_mode in order:
        if candidate_mode == 'EULER':
            from photonics.routing.euler_endpoint_solver import route_straight_euler_straight
            candidate = route_straight_euler_straight(
                source, destination, source_heading_deg, destination_heading_deg,
                min_radius_um=min_radius_um, samples=samples,
                position_tolerance_um=position_tolerance_um,
                heading_tolerance_deg=heading_tolerance_deg)
        else:
            if csc_router is None:
                attempts.append(('CSC', 'CSC_ROUTER_NOT_CONFIGURED'))
                continue
            candidate = csc_router(source, destination, source_heading_deg, destination_heading_deg)
        points, reason = _validate(candidate, source, destination,
                                   position_tolerance_um, clearance_check)
        attempts.append((candidate_mode, reason or 'PASS'))
        if points is not None:
            return SelectedRoute(True, candidate_mode, points, '', tuple(attempts))
    return SelectedRoute(False, 'NONE', (), 'NO_VALID_ROUTE', tuple(attempts))
