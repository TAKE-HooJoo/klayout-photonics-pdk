"""Extract hierarchical waveguide shapes as conservative bounding boxes.

The resulting obstacles are suitable for *screening*, not sign-off DRC.
"""
from photonics.routing.obstacles import Obstacle


def extract_waveguide_obstacles(cell, layout, layer_info=None):
    import pya
    if layer_info is None:
        layer_info = pya.LayerInfo(1, 0)
    layer_index = layout.find_layer(layer_info)
    if layer_index is None or layer_index < 0:
        return ()
    result = []
    # RecursiveShapeIterator applies instance transforms through itr.trans().
    iterator = cell.begin_shapes_rec(layer_index)
    while not iterator.at_end():
        shape = iterator.shape()
        if shape.is_box() or shape.is_polygon() or shape.is_path():
            box = shape.bbox().transformed(iterator.trans())
            dbu = layout.dbu
            result.append(Obstacle(box.left*dbu, box.bottom*dbu,
                                   box.right*dbu, box.top*dbu))
        iterator.next()
    return tuple(result)
