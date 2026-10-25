"""Sampled polyline quality diagnostics; coordinates are in micrometres.

This module does not claim mathematical G1/G2 continuity from samples.
"""
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class QualityReport:
    point_count: int
    length_um: float
    max_turn_deg: float
    min_sampled_radius_um: float
    max_abs_curvature_per_um: float
    zero_length_segments: tuple
    sharp_vertices: tuple
    radius_violations: tuple
    sampled_curvature: tuple


def _xy(p):
    if hasattr(p, 'x') and hasattr(p, 'y'):
        return float(p.x), float(p.y)
    return float(p[0]), float(p[1])


def analyze_route(points, min_radius_um=5.0, turn_threshold_deg=5.0, epsilon=1e-9):
    """Inspect consecutive triples; no geometry changes or KLayout dependency.

    Returns curvature signed by turn direction, in 1/um. The three-point
    circumcircle is only a sampling-based approximation of local curvature.
    """
    xy = tuple(_xy(p) for p in points)
    if len(xy) < 2:
        raise ValueError('At least two points are required')
    if min_radius_um <= 0 or not (0 < turn_threshold_deg <= 180):
        raise ValueError('Invalid thresholds')
    lengths = [math.hypot(b[0]-a[0], b[1]-a[1]) for a,b in zip(xy,xy[1:])]
    zeros = tuple(i for i,d in enumerate(lengths) if d <= epsilon)
    if zeros:
        return QualityReport(len(xy),sum(lengths),0.0,math.inf,0.0,zeros,(),(),())
    turns=[]; radii=[]; curvature=[]; sharp=[]; violations=[]
    for i,(a,b,c) in enumerate(zip(xy,xy[1:],xy[2:]),start=1):
        ux,uy=b[0]-a[0],b[1]-a[1]
        vx,vy=c[0]-b[0],c[1]-b[1]
        cross=ux*vy-uy*vx
        dot=ux*vx+uy*vy
        angle=math.degrees(math.atan2(abs(cross),dot))
        turns.append(angle)
        if angle > turn_threshold_deg:
            sharp.append((i,angle))
        chord=math.hypot(c[0]-a[0],c[1]-a[1])
        if abs(cross) <= epsilon or chord <= epsilon:
            radius=math.inf if abs(cross) <= epsilon else 0.0
        else:
            radius=lengths[i-1]*lengths[i]*chord/(2.0*abs(cross))
        radii.append(radius)
        k=0.0 if math.isinf(radius) else math.copysign(1.0/radius,cross) if radius>0 else math.inf
        curvature.append((i,k))
        if radius < min_radius_um:
            violations.append((i,radius))
    return QualityReport(len(xy),sum(lengths),max(turns,default=0.0),
                         min(radii,default=math.inf),
                         max((abs(k) for _,k in curvature),default=0.0),
                         zeros,tuple(sharp),tuple(violations),tuple(curvature))
