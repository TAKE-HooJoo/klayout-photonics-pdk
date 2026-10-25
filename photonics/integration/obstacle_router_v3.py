"""Phase 3E-5.1 experimental G1 fillet postprocessor.

Fail-closed: an unsmoothable or obstructed path is invalid, never accepted as
'clean'. This is not a complete self-spacing or foundry DRC engine.
"""
import math
from photonics.routing.result import RouteResult
from photonics.routing.geometry import length, min_radius, tangent_errors, unit
from photonics.routing.continuity import sharp_corners
from photonics.routing.fillet import fillet_polyline
from photonics.integration.obstacle_router import route_region
from photonics.integration.obstacle_router_v2 import route_with_waypoints
from photonics.integration.clearance_klayout import check_route_clearance


def route_with_smooth_waypoints(start, end, source_outward, destination_outward,
                                cross_section, design_rules, layout, obstacle_region,
                                tangent_tolerance_deg=5.0, samples_per_arc=36,
                                waypoint_offsets_um=None, fillet_radius_um=None):
    base = route_with_waypoints(start, end, source_outward, destination_outward,
                                cross_section, design_rules, layout, obstacle_region,
                                tangent_tolerance_deg=tangent_tolerance_deg,
                                samples_per_arc=samples_per_arc,
                                waypoint_offsets_um=waypoint_offsets_um)
    if not base.valid:
        return base
    # A route with sampled CSC arcs has small per-sample turns. Filleting every
    # sampled point is inappropriate: restrict to corners exceeding tolerance.
    # For genuine CSC samples, any large corner may be at a waypoint seam.
    radius = (max(cross_section.min_bend_radius_um,
                  design_rules.min_bend_radius_um) if fillet_radius_um is None
              else fillet_radius_um)
    if not math.isfinite(radius) or radius <= 0:
        raise ValueError('Invalid fillet radius')
    # First diagnose. A route without large corners remains unchanged.
    if not sharp_corners(base.points, tangent_tolerance_deg):
        return base
    try:
        pts = fillet_polyline(base.points, radius, samples_per_arc,
                              min_turn_deg=tangent_tolerance_deg)
    except ValueError:
        return RouteResult((), 0., 0., math.inf, 180., 180., False,
                           'NONE', 'FILLET_GEOMETRY_INFEASIBLE')
    err0, err1 = tangent_errors(pts, unit(source_outward), unit(destination_outward))
    if max(err0, err1) > tangent_tolerance_deg:
        return RouteResult((), 0., 0., math.inf, err0, err1, False,
                           'NONE', 'FILLET_PORT_TANGENT_ERROR')
    geometry = route_region(pts, cross_section.width_um, layout)
    passes, _, _ = check_route_clearance(geometry, obstacle_region, layout, design_rules)
    if not passes:
        return RouteResult((), 0., 0., math.inf, err0, err1, False,
                           'NONE', 'FILLET_CLEARANCE_VIOLATION')
    if sharp_corners(pts, tangent_tolerance_deg):
        return RouteResult((), 0., 0., math.inf, err0, err1, False,
                           'NONE', 'FILLET_REMAINING_KINK')
    return RouteResult(pts, length(pts), radius, min_radius(pts), err0, err1,
                       True, 'WAYPOINT_FILLET')
