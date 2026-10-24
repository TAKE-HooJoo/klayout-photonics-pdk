"""Batch KLayout adapter for the independent Phase 3C RoutingEngine.

No GUI/plugin registration. Import pya only when creating a KLayout shape.
"""
from photonics.circuit.geometry import Point
from photonics.routing import RoutingEngine


def route_between_ports(cell, layout, source, destination, cross_section,
                        design_rules, layer_info=None):
    """Create a DPath between v6.1/v6.2 extracted OpticalPort objects.

    Returns RouteResult. On failure, the layout is left unchanged.
    Source/destination direction must be the native outward port vectors.
    """
    import pya

    if layer_info is None:
        layer_info = pya.LayerInfo(1, 0)
    for port in (source, destination):
        if abs(float(port.width) - cross_section.width_um) > 1e-6:
            raise ValueError('Port width differs from cross section')
    engine = RoutingEngine(cross_section, design_rules)
    start = Point(float(source.position.x), float(source.position.y))
    end = Point(float(destination.position.x), float(destination.position.y))
    result = engine.route(start, end, tuple(source.direction), tuple(destination.direction))
    if not result.valid:
        return result
    dpoints = [pya.DPoint(p.x, p.y) for p in result.points]
    cell.shapes(layout.layer(layer_info)).insert(pya.DPath(dpoints, cross_section.width_um))
    return result
