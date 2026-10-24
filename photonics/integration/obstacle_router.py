"""KLayout-aware CSC route selection with exact-region clearance screening.

No shapes are inserted. Ports use native outward direction vectors.
"""
import math

from photonics.circuit.geometry import Point
from photonics.routing.dubins import words, candidate, mod2pi
from photonics.routing.geometry import unit, length, min_radius, tangent_errors
from photonics.routing.result import RouteResult
from photonics.integration.clearance_klayout import check_route_clearance


def _failed(reason):
    return RouteResult((), 0., 0., math.inf, 180., 180., False, 'NONE', reason)


def route_region(points, width_um, layout):
    """Convert a sampled route centreline into a waveguide Region."""
    import pya
    if len(points) < 2:
        raise ValueError('At least two points are required')
    if not math.isfinite(width_um) or width_um <= 0:
        raise ValueError('Invalid waveguide width')
    path = pya.DPath([pya.DPoint(p.x, p.y) for p in points], width_um)
    return pya.Region(path.to_itype(layout.dbu).polygon())


def route_avoiding_obstacles(start, end, source_outward, destination_outward,
                             cross_section, design_rules, layout, obstacle_region,
                             tangent_tolerance_deg=5.0, samples_per_arc=36):
    """Return shortest legal, clearance-clean straight/CSC route.

    The obstacle_region must exclude or appropriately clip the intended source
    and destination connection geometry; this routine never silently exempts it.
    Candidate sampling and arc restrictions match RoutingEngine.route().
    """
    import pya
    if not isinstance(obstacle_region, pya.Region):
        raise TypeError('obstacle_region must be a pya.Region')
    if not design_rules.validate_cross_section(cross_section):
        raise ValueError('Cross section violates design rules')
    if not (0 < tangent_tolerance_deg < 90) or samples_per_arc < 4:
        raise ValueError('Invalid routing configuration')
    if not all(math.isfinite(v) for v in (start.x, start.y, end.x, end.y)):
        raise ValueError('Coordinates must be finite')
    src = unit(source_outward)
    dst = unit(destination_outward)
    arrival = (-dst[0], -dst[1])
    dx, dy = end.x - start.x, end.y - start.y
    distance = math.hypot(dx, dy)
    if distance < 1e-9:
        return _failed('COINCIDENT_PORTS')

    legal = []
    chord = (dx / distance, dy / distance)
    if (chord[0]*src[0] + chord[1]*src[1] > 1 - 1e-12 and
            chord[0]*arrival[0] + chord[1]*arrival[1] > 1 - 1e-12):
        legal.append(RouteResult((start, end), distance, math.inf, math.inf,
                                 0., 0., True, 'STRAIGHT'))
    else:
        radius = max(cross_section.min_bend_radius_um,
                     design_rules.min_bend_radius_um) * 1.25
        theta = math.atan2(dy, dx)
        alpha = mod2pi(math.atan2(src[1], src[0]) - theta)
        beta = mod2pi(math.atan2(arrival[1], arrival[0]) - theta)
        for word, t, p, q in words(alpha, beta, distance/radius):
            if math.degrees(t + q) > 240:
                continue
            pts = candidate(start, end, src, arrival, radius, word, t, p, q,
                            samples_per_arc)
            if pts is None:
                continue
            err0, err1 = tangent_errors(pts, src, dst)
            if max(err0, err1) > tangent_tolerance_deg:
                continue
            plen = length(pts)
            if plen > 2.2 * distance:
                continue
            legal.append(RouteResult(pts, plen, radius, min_radius(pts),
                                     err0, err1, True, word))

    if not legal:
        return _failed('NO_LEGAL_CSC_ROUTE')
    for route in sorted(legal, key=lambda item: item.length_um):
        region = route_region(route.points, cross_section.width_um, layout)
        passes, _, _ = check_route_clearance(region, obstacle_region,
                                              layout, design_rules)
        if passes:
            return route
    return _failed('ALL_CANDIDATES_BLOCKED')
