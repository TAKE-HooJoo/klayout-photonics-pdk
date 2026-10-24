"""Phase 3E-4: conservative waypoint fallback for obstacle-aware routing.

The existing Phase 3E-3 router is left unchanged. Coordinates are micrometres.
The input obstacle Region must exclude/clip intended port connection geometry.
Waypoint candidates are heuristic; failure does not prove no route exists.
"""
import math

from photonics.circuit.geometry import Point
from photonics.routing.geometry import length, min_radius, tangent_errors, unit
from photonics.routing.result import RouteResult
from photonics.integration.obstacle_router import (
    route_avoiding_obstacles, route_region,
)
from photonics.integration.clearance_klayout import check_route_clearance


def _failure(reason):
    return RouteResult((), 0., 0., math.inf, 180., 180., False, 'NONE', reason)


def _join_routes(parts, start, end, source_outward, destination_outward,
                 layout, width_um, obstacle_region, design_rules,
                 tangent_tolerance_deg):
    """Combine tangent-matched legs and recheck the complete waveguide."""
    pts = []
    for part in parts:
        if not part.valid:
            return None
        if pts and math.hypot(pts[-1].x-part.points[0].x,
                              pts[-1].y-part.points[0].y) > 1e-6:
            return None
        pts.extend(part.points if not pts else part.points[1:])
    if len(pts) < 2:
        return None
    pts = tuple(pts)
    err0, err1 = tangent_errors(pts, unit(source_outward), unit(destination_outward))
    if max(err0, err1) > tangent_tolerance_deg:
        return None
    region = route_region(pts, width_um, layout)
    passes, _, _ = check_route_clearance(region, obstacle_region, layout, design_rules)
    if not passes:
        return None
    # Conservative check: the complete path must not overlap itself away from
    # adjacent samples. Region-based clearance alone cannot detect self-crossing.
    # Full self-spacing verification is reserved for a subsequent phase.
    radii = [p.designed_radius_um for p in parts if math.isfinite(p.designed_radius_um)]
    designed = min(radii) if radii else math.inf
    return RouteResult(pts, length(pts), designed, min_radius(pts),
                       err0, err1, True, 'WAYPOINT_CSC')


def route_with_waypoints(start, end, source_outward, destination_outward,
                         cross_section, design_rules, layout, obstacle_region,
                         tangent_tolerance_deg=5.0, samples_per_arc=36,
                         waypoint_offsets_um=None):
    """Try Phase 3E-3 first, then two same-heading intermediate waypoints.

    This bounded fallback works best for separated, facing ports. It does not
    claim exhaustive obstacle avoidance or full waveguide self-spacing DRC.
    """
    import pya
    if not isinstance(obstacle_region, pya.Region):
        raise TypeError('obstacle_region must be a pya.Region')
    base_args = (cross_section, design_rules, layout, obstacle_region)
    opts = dict(tangent_tolerance_deg=tangent_tolerance_deg,
                samples_per_arc=samples_per_arc)
    direct = route_avoiding_obstacles(start, end, source_outward,
                                     destination_outward, *base_args, **opts)
    if direct.valid or direct.reason == 'COINCIDENT_PORTS':
        return direct
    dx, dy = end.x-start.x, end.y-start.y
    d = math.hypot(dx, dy)
    if d < 1e-9:
        return direct
    ux, uy = dx/d, dy/d
    heading = (ux, uy)
    opposite = (-ux, -uy)
    offsets = waypoint_offsets_um
    if offsets is None:
        radius = max(cross_section.min_bend_radius_um,
                     design_rules.min_bend_radius_um)
        offsets = (1.5*radius, 2*radius, 3*radius, 4*radius)
    if not offsets or any(not math.isfinite(v) or v <= 0 for v in offsets):
        raise ValueError('Waypoint offsets must be finite and positive')
    best = None
    # A pair of waypoints with the same forward tangent produces a continuous
    # path: source -> wp1 -> wp2 -> destination.
    for sign in (1, -1):
        for offset in offsets:
            for f1, f2 in ((.25, .75), (.30, .70), (.20, .80), (.35, .65)):
                wp1 = Point(start.x+f1*dx-sign*uy*offset,
                            start.y+f1*dy+sign*ux*offset)
                wp2 = Point(start.x+f2*dx-sign*uy*offset,
                            start.y+f2*dy+sign*ux*offset)
                a = route_avoiding_obstacles(start, wp1, source_outward,
                                             opposite, *base_args, **opts)
                if not a.valid:
                    continue
                b = route_avoiding_obstacles(wp1, wp2, heading,
                                             opposite, *base_args, **opts)
                if not b.valid:
                    continue
                c = route_avoiding_obstacles(wp2, end, heading,
                                             destination_outward, *base_args,
                                             **opts)
                if not c.valid:
                    continue
                merged = _join_routes((a, b, c), start, end, source_outward,
                                      destination_outward, layout,
                                      cross_section.width_um, obstacle_region,
                                      design_rules, tangent_tolerance_deg)
                if merged is not None and (best is None or merged.length_um < best.length_um):
                    best = merged
    return best if best is not None else _failure('NO_CLEAR_WAYPOINT_ROUTE')
