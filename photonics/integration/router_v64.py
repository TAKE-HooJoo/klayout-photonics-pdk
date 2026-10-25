"""Experimental v6.4 obstacle-aware GUI adapter (coordinates in um).

The small endpoint exclusion boxes are connection windows, not a foundry DRC
waiver. A full device-aware port clearance model is future work.
"""
import math
from photonics.circuit.geometry import Point
from photonics.integration.clearance_klayout import waveguide_region, check_route_clearance
from photonics.integration.obstacle_router import route_region
from photonics.integration.obstacle_router_v2 import route_with_waypoints
from photonics.routing.geometry import min_radius, tangent_errors, unit
from photonics.routing.continuity import sharp_corners


def route_between_ports_v64(cell, layout, source, destination, xs, rules,
                            waveguide_layer=None, connection_window_um=None,
                            obstacle_layer=None):
    import pya
    if not rules.validate_cross_section(xs):
        raise ValueError('INVALID_CROSS_SECTION')
    if abs(float(source.width) - float(destination.width)) > 1e-6:
        raise ValueError('PORT_WIDTH_MISMATCH')
    if abs(float(source.width) - xs.width_um) > 1e-6:
        raise ValueError('CROSS_SECTION_WIDTH_MISMATCH')
    a = Point(float(source.position.x), float(source.position.y))
    b = Point(float(destination.position.x), float(destination.position.y))
    if math.hypot(a.x-b.x, a.y-b.y) < 1e-9:
        raise ValueError('COINCIDENT_PORTS')
    if connection_window_um is None:
        connection_window_um = max(xs.width_um, rules.min_waveguide_spacing_um) + xs.width_um
    if not math.isfinite(connection_window_um) or connection_window_um <= 0:
        raise ValueError('INVALID_CONNECTION_WINDOW')
    if waveguide_layer is None:
        waveguide_layer = pya.LayerInfo(1, 0)
    if obstacle_layer is None:
        obstacle_layer = pya.LayerInfo(90, 0)
    original = waveguide_region(cell, layout, waveguide_layer)
    # Clip only the two tiny port-connection windows. All other existing
    # waveguide geometry, including hierarchical PCells, remains an obstacle.
    cut = pya.Region()
    for p in (a, b):
        h = connection_window_um
        cut.insert(pya.DBox(p.x-h, p.y-h, p.x+h, p.y+h).to_itype(layout.dbu))
    # Only the WG layer receives port connection exemptions. Dedicated
    # keepout polygons must never be clipped around ports.
    obstacles = original - cut
    obstacle_index = layout.find_layer(obstacle_layer)
    if obstacle_index is not None and obstacle_index >= 0:
        obstacles += pya.Region(cell.begin_shapes_rec(obstacle_index)).merged()
    obstacles.merge()
    result = route_with_waypoints(a, b, unit(source.direction),
                                  unit(destination.direction), xs, rules,
                                  layout, obstacles)
    if not result.valid:
        return result
    # Reject undersampled sharp corners and insufficient sampled radius.
    if sharp_corners(result.points, 5.0):
        raise ValueError('ROUTE_SHARP_CORNER')
    radius = min_radius(result.points)
    if radius + 1e-6 < rules.min_bend_radius_um:
        raise ValueError('ROUTE_BEND_RADIUS')
    e0, e1 = tangent_errors(result.points, unit(source.direction),
                            unit(destination.direction))
    if max(e0, e1) > 5.0:
        raise ValueError('ROUTE_PORT_TANGENT')
    geometry = route_region(result.points, xs.width_um, layout)
    ok, _, _ = check_route_clearance(geometry, obstacles, layout, rules)
    if not ok:
        raise ValueError('ROUTE_CLEARANCE')
    # One final overlap check against original obstacles outside the two
    # endpoint windows. This does not establish clearance inside windows.
    if not (geometry & obstacles).is_empty():
        raise ValueError('ROUTE_OVERLAP')
    layer_index = layout.layer(waveguide_layer)
    # Mutation happens only after every validation has passed.
    cell.shapes(layer_index).insert(geometry)
    return result
