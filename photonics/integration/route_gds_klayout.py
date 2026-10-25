"""Phase 3E-5: explicit, validated GDS export of a routed waveguide.

The obstacle layer is a *visualization* layer, not a foundry PDK layer.
Input obstacle Region must already exclude/clip intended port connections.
"""
import math
from photonics.integration.obstacle_router import route_region
from photonics.integration.clearance_klayout import check_route_clearance


def export_route_gds(route, cross_section, design_rules, obstacle_region,
                     output_path, dbu=0.001, top_name='PHOTONICS_ROUTE_TEG',
                     port_length_um=1.0):
    """Create a new layout and export a clearance-checked route to GDS.

    Returns a dict of route metadata. Does not modify the original layout.
    Obstacles are written on 90/0 for *visual inspection only*.
    """
    import pya
    if not route.valid or len(route.points) < 2:
        raise ValueError('Cannot export an invalid or empty route')
    if not design_rules.validate_cross_section(cross_section):
        raise ValueError('Cross section violates design rules')
    if not isinstance(obstacle_region, pya.Region):
        raise TypeError('obstacle_region must be a pya.Region')
    if not math.isfinite(dbu) or dbu <= 0:
        raise ValueError('dbu must be finite and positive')
    if not math.isfinite(port_length_um) or port_length_um <= 0:
        raise ValueError('port_length_um must be finite and positive')
    layout = pya.Layout()
    layout.dbu = dbu
    top = layout.create_cell(top_name)
    waveguide_layer = layout.layer(pya.LayerInfo(1, 0))
    port_layer = layout.layer(pya.LayerInfo(2, 0))
    obstacle_layer = layout.layer(pya.LayerInfo(90, 0))

    geometry = route_region(route.points, cross_section.width_um, layout)
    passes, overlap, near = check_route_clearance(
        geometry, obstacle_region, layout, design_rules)
    if not passes:
        raise ValueError('Route violates obstacle clearance; GDS not written')

    # Write the exact same polygonal Region used for clearance checking.
    top.shapes(waveguide_layer).insert(geometry)
    top.shapes(obstacle_layer).insert(obstacle_region)

    # Port markers: short centreline paths aligned with first/last route segments.
    for a, b in ((route.points[0], route.points[1]),
                 (route.points[-2], route.points[-1])):
        dx, dy = b.x - a.x, b.y - a.y
        dist = math.hypot(dx, dy)
        if dist < 1e-12:
            raise ValueError('Degenerate endpoint segment')
        ux, uy = dx / dist, dy / dist
        anchor = a if a == route.points[0] else b
        p1 = pya.DPoint(anchor.x - ux*port_length_um/2,
                        anchor.y - uy*port_length_um/2)
        p2 = pya.DPoint(anchor.x + ux*port_length_um/2,
                        anchor.y + uy*port_length_um/2)
        top.shapes(port_layer).insert(
            pya.DPath([p1, p2], cross_section.width_um).to_itype(layout.dbu))

    layout.write(str(output_path))
    return {'path': str(output_path), 'top': top_name,
            'variant': route.variant, 'length_um': route.length_um,
            'points': len(route.points), 'clearance_pass': passes,
            'waveguide_layer': '1/0', 'port_layer': '2/0',
            'obstacle_layer': '90/0'}
