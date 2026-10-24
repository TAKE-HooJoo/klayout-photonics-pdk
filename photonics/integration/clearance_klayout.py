"""KLayout Region-based waveguide clearance screening (units: um).

This module deliberately does not change the existing router. Clearance
violations are conservative at the database grid and need DRC review.
"""
import math


def _distance_dbu(layout, spacing_um):
    if not math.isfinite(spacing_um) or spacing_um <= 0:
        raise ValueError('spacing_um must be finite and positive')
    return max(1, int(math.ceil(spacing_um / layout.dbu)))


def waveguide_region(cell, layout, layer_info=None):
    """Return merged waveguide geometry, including transformed child cells."""
    import pya
    if layer_info is None:
        layer_info = pya.LayerInfo(1, 0)
    layer_index = layout.find_layer(layer_info)
    if layer_index is None or layer_index < 0:
        return pya.Region()
    return pya.Region(cell.begin_shapes_rec(layer_index)).merged()


def clearance_violations(route_region, obstacle_region, layout, spacing_um):
    """Return regions for overlap and insufficient edge clearance.

    This treats touching boundaries as violations. An integer DBU dilation is
    conservative by at most one grid unit in the distance threshold.
    The caller must explicitly exclude or clip intended port connections.
    """
    import pya
    if not isinstance(route_region, pya.Region) or not isinstance(obstacle_region, pya.Region):
        raise TypeError('route_region and obstacle_region must be pya.Region')
    delta = _distance_dbu(layout, spacing_um)
    overlap = route_region & obstacle_region
    # Positive sizing of route captures nearby obstacle geometry.
    near = route_region.sized(delta) & obstacle_region
    return overlap, near


def check_route_clearance(route_region, obstacle_region, layout, design_rules):
    """Return (passes, overlap_region, violation_region)."""
    overlap, near = clearance_violations(
        route_region, obstacle_region, layout,
        design_rules.min_waveguide_spacing_um)
    return near.is_empty() and overlap.is_empty(), overlap, near
