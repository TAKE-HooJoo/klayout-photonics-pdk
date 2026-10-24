import math
from photonics.circuit.geometry import Point

def unit(v):
    n = math.hypot(*v)
    if not math.isfinite(n) or n <= 1e-12:
        raise ValueError('Direction must be finite and nonzero')
    return (v[0] / n, v[1] / n)

def length(points):
    return sum(math.hypot(b.x-a.x, b.y-a.y) for a,b in zip(points,points[1:]))

def radius(a,b,c):
    ab=math.hypot(a.x-b.x,a.y-b.y)
    bc=math.hypot(b.x-c.x,b.y-c.y)
    ca=math.hypot(c.x-a.x,c.y-a.y)
    area2=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))
    if min(ab,bc,ca)<1e-12 or area2<1e-12:
        return math.inf
    return ab*bc*ca/(2*area2)

def min_radius(points):
    return min((radius(a,b,c) for a,b,c in zip(points,points[1:],points[2:])),default=math.inf)

def angle_error(v,w):
    a,b=unit(v),unit(w)
    return math.degrees(math.acos(max(-1,min(1,a[0]*b[0]+a[1]*b[1]))))

def tangent_errors(points,src,dst):
    if len(points)<2:
        return (180.,180.)
    a,b=points[0],points[1]
    c,d=points[-2],points[-1]
    return (angle_error((b.x-a.x,b.y-a.y),src),angle_error((d.x-c.x,d.y-c.y),(-dst[0],-dst[1])))
