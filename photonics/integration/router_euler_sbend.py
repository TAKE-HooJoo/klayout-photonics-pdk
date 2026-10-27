"""Phase 3E-7.7B: fail-closed KLayout adapter for pure Python Euler S-bend.

This module does not modify a cell until all validations pass.
Port headings are TRAVEL headings (destination outward port heading + 180 deg).
"""
from dataclasses import dataclass
import math
import pya
from photonics.routing.euler_sbend import route_euler_sbend


@dataclass(frozen=True)
class SBendLayoutResult:
    valid: bool
    reason: str
    variant: str
    length_um: float
    designed_radius_um: float
    sampled_radius_um: float
    endpoint_error_um: float
    tangent_error_source_deg: float
    tangent_error_destination_deg: float
    points: tuple


def _angle_error(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def _sampled_radius(points):
    radii = []
    for a, b, c in zip(points, points[1:], points[2:]):
        ab = math.dist(a, b)
        bc = math.dist(b, c)
        ac = math.dist(a, c)
        twice_area = abs((b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]))
        if min(ab, bc, ac) < 1e-10 or twice_area < 1e-12:
            continue
        radii.append(ab*bc*ac/(2.0*twice_area))
    return min(radii) if radii else math.inf


def _end_tangent(points, start):
    pairs = zip(points, points[1:])
    if not start:
        pairs = ((b, a) for a, b in zip(points[::-1], points[-2::-1]))
    for a, b in pairs:
        dx, dy = b[0]-a[0], b[1]-a[1]
        if math.hypot(dx, dy) > 1e-10:
            return math.degrees(math.atan2(dy, dx))
    return math.nan


def _fail(reason, points=()):
    return SBendLayoutResult(False, reason, 'EULER_SBEND', 0.0, 0.0,
                             math.inf, math.inf, math.inf, math.inf, tuple(points))


def route_euler_sbend_klayout(cell, layout, source, destination,
                               source_heading_deg, destination_heading_deg,
                               waveguide_layer=(1, 0), width_um=0.5,
                               min_radius_um=6.25, obstacle_region=None,
                               obstacle_layer=None, clearance_um=0.0,
                               samples_per_bend=201, tangent_tolerance_deg=5.0,
                               radius_tolerance_fraction=0.02):
    """Place one S-bend after validation. All distances in um.

    `obstacle_region` must be a pya.Region in integer database units (DBU).
    `obstacle_layer` may specify a separate keepout layer (e.g. (90,0)).
    Existing waveguides are not automatically treated as obstacles: supply
    them explicitly in obstacle_region if that behavior is desired.
    This adapter does NOT waive any obstacle around the connection ports.
    """
    if not math.isfinite(width_um) or width_um <= 0:
        raise ValueError('width_um must be positive and finite')
    if not math.isfinite(clearance_um) or clearance_um < 0:
        raise ValueError('clearance_um must be nonnegative and finite')
    if not 0 <= radius_tolerance_fraction < 1:
        raise ValueError('radius_tolerance_fraction must be in [0,1)')
    if not math.isfinite(layout.dbu) or layout.dbu <= 0:
        raise ValueError('layout.dbu must be positive')
    result = route_euler_sbend(source, destination, source_heading_deg,
                               destination_heading_deg,
                               min_radius_um=min_radius_um,
                               samples_per_bend=samples_per_bend)
    if not result.valid:
        return _fail(result.reason)
    points = tuple(result.points)
    if len(points) < 2:
        return _fail('TOO_FEW_POINTS', points)
    if result.endpoint_error_um > 0.01:
        return _fail('ENDPOINT_MISMATCH', points)
    src_tan = _end_tangent(points, True)
    dst_tan = _end_tangent(points, False)
    src_err = _angle_error(src_tan, source_heading_deg)
    dst_err = _angle_error(dst_tan, destination_heading_deg)
    if src_err > tangent_tolerance_deg or dst_err > tangent_tolerance_deg:
        return _fail('TANGENT_MISMATCH', points)
    measured = _sampled_radius(points)
    # A polyline's circumcircle estimate is an approximation, not a foundry DRC.
    if measured < min_radius_um * (1.0-radius_tolerance_fraction):
        return _fail('SAMPLED_RADIUS_BELOW_MINIMUM', points)
    dbu = layout.dbu
    ipoints = [pya.Point(int(round(x/dbu)), int(round(y/dbu))) for x,y in points]
    dedup = [ipoints[0]]
    for pt in ipoints[1:]:
        if pt != dedup[-1]:
            dedup.append(pt)
    if len(dedup) < 2:
        return _fail('DEGENERATE_AFTER_QUANTIZATION', points)
    width_dbu = max(1, int(round(width_um/dbu)))
    polygon = pya.Path(dedup, width_dbu).polygon()
    candidate = pya.Region(polygon)
    obstacles = pya.Region()
    if obstacle_region is not None:
        obstacles += obstacle_region
    if obstacle_layer is not None:
        keepout_index = layout.layer(*obstacle_layer)
        obstacles += pya.Region(cell.begin_shapes_rec(keepout_index))
    if not obstacles.is_empty():
        clearance_dbu = int(math.ceil(clearance_um/dbu))
        if clearance_dbu:
            candidate = candidate.sized(clearance_dbu)
        if not (candidate & obstacles).is_empty():
            return _fail('OBSTACLE_CLEARANCE_VIOLATION', points)
    # Only side effect on the cell: one final insert after every check.
    cell.shapes(layout.layer(*waveguide_layer)).insert(polygon)
    return SBendLayoutResult(True, '', 'EULER_SBEND', result.length_um,
                             result.min_radius_um, measured,
                             result.endpoint_error_um, src_err, dst_err, points)
