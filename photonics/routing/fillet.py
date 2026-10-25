"""Circular fillets at polyline vertices with tangent-continuous transitions.

A polyline is not intrinsically curvature continuous; this constructs G1 arcs.
Each arc uses the requested radius and exact tangent points. The caller must
check full-route obstacle clearance and route self-intersections separately.
"""
import math
from photonics.circuit.geometry import Point
from photonics.routing.geometry import length


def fillet_polyline(points, radius_um, samples_per_arc=24, min_turn_deg=2.0):
    pts = tuple(points)
    if len(pts) < 2:
        raise ValueError('At least two points required')
    if not math.isfinite(radius_um) or radius_um <= 0 or samples_per_arc < 4:
        raise ValueError('Invalid fillet configuration')
    if not 0 <= min_turn_deg < 90:
        raise ValueError('Invalid minimum turn angle')
    if len(pts) == 2:
        return pts
    segments = []
    for a, b in zip(pts, pts[1:]):
        dx, dy = b.x-a.x, b.y-a.y
        n = math.hypot(dx, dy)
        if n <= 1e-10:
            raise ValueError('Degenerate segment')
        segments.append((dx/n, dy/n, n))
    corners = []
    for i in range(1, len(pts)-1):
        ux, uy, l0 = segments[i-1]
        vx, vy, l1 = segments[i]
        theta = math.atan2(ux*vy-uy*vx, ux*vx+uy*vy)
        if abs(math.degrees(theta)) < min_turn_deg:
            corners.append(None)
            continue
        if abs(theta) >= math.pi-1e-6:
            raise ValueError('Near U-turn cannot be filleted')
        tangent_distance = radius_um*math.tan(abs(theta)/2)
        corners.append((theta, tangent_distance))
    # Check shared segment has enough length for both neighboring fillets.
    for i, (_, _, seglen) in enumerate(segments):
        incoming = corners[i-1][1] if i > 0 and corners[i-1] else 0.0
        outgoing = corners[i][1] if i < len(corners) and corners[i] else 0.0
        if incoming+outgoing >= seglen-1e-8:
            raise ValueError('Insufficient straight lead for fillet radius')
    result = [pts[0]]
    for i, info in enumerate(corners, 1):
        if info is None:
            result.append(pts[i])
            continue
        theta, d = info
        ux, uy, _ = segments[i-1]
        vx, vy, _ = segments[i]
        vertex = pts[i]
        start = Point(vertex.x-d*ux, vertex.y-d*uy)
        end = Point(vertex.x+d*vx, vertex.y+d*vy)
        sign = 1 if theta > 0 else -1
        cx = start.x-sign*radius_um*uy
        cy = start.y+sign*radius_um*ux
        a0 = math.atan2(start.y-cy, start.x-cx)
        result.append(start)
        n = max(samples_per_arc, int(math.ceil(abs(theta)*samples_per_arc/(math.pi/2))))
        for k in range(1, n):
            angle = a0+theta*k/n
            result.append(Point(cx+radius_um*math.cos(angle), cy+radius_um*math.sin(angle)))
        result.append(end)
    result.append(pts[-1])
    return tuple(result)
