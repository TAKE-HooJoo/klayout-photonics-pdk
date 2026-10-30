"""Experimental v6.5 CSC/Euler/AUTO KLayout adapter; no changes to v6.4.

Only the selected, validated route is inserted. Positions are micrometers.
Port directions are OUTWARD from the device: the destination arrival heading
is opposite its outward vector. Endpoint connection windows waive WG geometry
only, never dedicated keepout shapes. Not a foundry DRC signoff.
"""
import math
from photonics.circuit.geometry import Point
from photonics.routing.result import RouteResult
from photonics.routing.geometry import length, min_radius, tangent_errors, unit
from photonics.routing.continuity import sharp_corners
from photonics.routing.euler_endpoint_solver import route_straight_euler_straight
from photonics.routing.euler_sbend import route_euler_sbend
from photonics.routing.route_quality import evaluate_route_quality
from photonics.integration.obstacle_router_v2 import route_with_waypoints
from photonics.integration.obstacle_router import route_region
from photonics.integration.clearance_klayout import waveguide_region, check_route_clearance


def _failure(reason):
    return RouteResult((), 0.0, 0.0, math.inf, 180.0, 180.0, False, 'NONE', reason)


def _heading(v):
    return math.degrees(math.atan2(v[1], v[0]))


def _euler_candidate(a, b, src, dst, radius, samples):
    # dst is outward; Euler expects direction of travel upon ARRIVAL.
    r = route_straight_euler_straight(
        (a.x, a.y), (b.x, b.y), _heading(src),
        _heading((-dst[0], -dst[1])), min_radius_um=radius,
        samples=samples)
    if not r.valid:
        return _failure(r.reason)
    pts = tuple(Point(x, y) for x, y in r.points)
    e0, e1 = tangent_errors(pts, src, dst)
    return RouteResult(pts, length(pts), radius, min_radius(pts),
                       e0, e1, True, 'EULER')


def _sbend_candidate(a, b, src, dst, radius, samples):
    # Port directions are outward; arrival travel heading is -dst.
    r = route_euler_sbend(
        (a.x, a.y), (b.x, b.y), _heading(src),
        _heading((-dst[0], -dst[1])), min_radius_um=radius,
        samples_per_bend=max(5, (samples + 1) // 2))
    if not r.valid:
        return _failure(r.reason)
    pts = tuple(Point(x, y) for x, y in r.points)
    e0, e1 = tangent_errors(pts, src, dst)
    return RouteResult(pts, length(pts), radius, min_radius(pts),
                       e0, e1, True, 'EULER_SBEND')


def route_between_ports_hybrid(cell, layout, source, destination, xs, rules,
                               mode='AUTO', waveguide_layer=None,
                               obstacle_layer=None, connection_window_um=None,
                               samples=401, tangent_tolerance_deg=5.0):
    """Select, validate, then place once. Returns RouteResult.

    No mutations occur on failed routing, other than KLayout's possible
    registration of layer indices during a successful final insertion.
    """
    import pya
    mode = str(mode).upper()
    if mode not in ('CSC', 'EULER', 'AUTO', 'AUTO_QUALITY'):
        raise ValueError('INVALID_MODE')
    if not rules.validate_cross_section(xs):
        raise ValueError('INVALID_CROSS_SECTION')
    if abs(float(source.width) - float(destination.width)) > 1e-6:
        raise ValueError('PORT_WIDTH_MISMATCH')
    if abs(float(source.width) - xs.width_um) > 1e-6:
        raise ValueError('CROSS_SECTION_WIDTH_MISMATCH')
    if not isinstance(samples, int) or samples < 3:
        raise ValueError('INVALID_SAMPLES')
    if not (0 < tangent_tolerance_deg < 90):
        raise ValueError('INVALID_TANGENT_TOLERANCE')
    a = Point(float(source.position.x), float(source.position.y))
    b = Point(float(destination.position.x), float(destination.position.y))
    if not all(map(math.isfinite, (a.x, a.y, b.x, b.y))):
        raise ValueError('INVALID_PORT_POSITION')
    if math.hypot(a.x-b.x, a.y-b.y) < 1e-9:
        return _failure('COINCIDENT_PORTS')
    src, dst = unit(source.direction), unit(destination.direction)
    if connection_window_um is None:
        connection_window_um = max(xs.width_um, rules.min_waveguide_spacing_um) + xs.width_um
    if not math.isfinite(connection_window_um) or connection_window_um <= 0:
        raise ValueError('INVALID_CONNECTION_WINDOW')
    waveguide_layer = waveguide_layer or pya.LayerInfo(1, 0)
    obstacle_layer = obstacle_layer or pya.LayerInfo(90, 0)
    original = waveguide_region(cell, layout, waveguide_layer)
    cut = pya.Region()
    for p in (a, b):
        h = connection_window_um
        cut.insert(pya.DBox(p.x-h, p.y-h, p.x+h, p.y+h).to_itype(layout.dbu))
    obstacles = original - cut
    keepout_index = layout.find_layer(obstacle_layer)
    if keepout_index is not None and keepout_index >= 0:
        obstacles += pya.Region(cell.begin_shapes_rec(keepout_index)).merged()
    obstacles.merge()
    radius_limit = max(xs.min_bend_radius_um, rules.min_bend_radius_um)
    attempts = ('SBEND', 'EULER', 'CSC') if mode in ('AUTO', 'AUTO_QUALITY') else (('SBEND', 'EULER') if mode == 'EULER' else ('CSC',))
    accepted = []
    last_reason = 'NO_VALID_ROUTE'
    for name in attempts:
        if name == 'SBEND':
            candidate = _sbend_candidate(a, b, src, dst, radius_limit, samples)
        elif name == 'EULER':
            candidate = _euler_candidate(a, b, src, dst, radius_limit, samples)
        else:
            candidate = route_with_waypoints(a, b, src, dst, xs, rules,
                                             layout, obstacles,
                                             tangent_tolerance_deg=tangent_tolerance_deg)
        if not candidate.valid:
            last_reason = candidate.reason or 'NO_ROUTE'
            continue
        pts = candidate.points
        if len(pts) < 2 or any(not (math.isfinite(p.x) and math.isfinite(p.y)) for p in pts):
            last_reason = 'INVALID_POINTS'
            continue
        if math.hypot(pts[0].x-a.x, pts[0].y-a.y) > .01 or math.hypot(pts[-1].x-b.x, pts[-1].y-b.y) > .01:
            last_reason = 'ENDPOINT_MISMATCH'
            continue
        if sharp_corners(pts, 5.0):
            last_reason = 'ROUTE_SHARP_CORNER'
            continue
        sampled_radius = min_radius(pts)
        # Sampled three-point radius is a diagnostic. v6.4 uses this guard.
        if sampled_radius + 1e-6 < rules.min_bend_radius_um:
            last_reason = 'ROUTE_BEND_RADIUS'
            continue
        if candidate.designed_radius_um + 1e-6 < radius_limit:
            last_reason = 'DESIGNED_RADIUS'
            continue
        e0, e1 = tangent_errors(pts, src, dst)
        if max(e0, e1) > tangent_tolerance_deg:
            last_reason = 'ROUTE_PORT_TANGENT'
            continue
        geometry = route_region(pts, xs.width_um, layout)
        ok, _, _ = check_route_clearance(geometry, obstacles, layout, rules)
        if not ok or not (geometry & obstacles).is_empty():
            last_reason = 'ROUTE_CLEARANCE'
            continue
        # No layout mutation until the chosen candidate is known.
        result = RouteResult(tuple(pts), length(pts), candidate.designed_radius_um,
                             sampled_radius, e0, e1, True,
                             ('EULER_SBEND' if name == 'SBEND' else ('EULER' if name == 'EULER' else candidate.variant)))
        if mode != 'AUTO_QUALITY':
            cell.shapes(layout.layer(waveguide_layer)).insert(geometry)
            return result
        try:
            quality = evaluate_route_quality(pts)
        except ValueError:
            last_reason = 'INVALID_QUALITY_GEOMETRY'
            continue
        accepted.append((result, geometry, quality))
    if mode == 'AUTO_QUALITY' and accepted:
        # Normalize by the best candidate in this set. Both terms are
        # dimensionless; equal weights are a provisional geometric heuristic.
        # The polygonal energy is sampling-dependent, NOT optical loss.
        length_ref = min(item[2].length_um for item in accepted)
        energy_ref = max(item[2].curvature_energy_inv_um for item in accepted)
        def score(item):
            q = item[2]
            energy_term = (q.curvature_energy_inv_um / energy_ref
                           if energy_ref > 0 else 0.0)
            return (q.length_um / length_ref + energy_term,
                    q.length_um, item[0].variant)
        chosen = min(accepted, key=score)
        cell.shapes(layout.layer(waveguide_layer)).insert(chosen[1])
        return chosen[0]
    return _failure(last_reason)
