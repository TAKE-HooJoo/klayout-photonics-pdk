"""Phase 3E-7.8C-1: dependency-free, diagnostic route quality metrics.

Coordinates and arc lengths are in um. Curvature is in 1/um.
The polygonal estimator is NOT an exact curvature or optical-loss model.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class RouteQuality:
    length_um: float
    max_abs_curvature_inv_um: float
    min_sampled_radius_um: float
    curvature_energy_inv_um: float
    max_sampled_delta_curvature_inv_um: float
    max_declared_jump_inv_um: float
    point_count: int


def _xy(point):
    if hasattr(point, 'x') and hasattr(point, 'y'):
        return float(point.x), float(point.y)
    return float(point[0]), float(point[1])


def evaluate_route_quality(points, curvature_jumps=()):
    """Evaluate a sampled centerline, with optional known curvature jumps.

    `curvature_jumps` is a sequence of signed curvature differences (1/um)
    supplied by the exact route topology, e.g. CSC straight/arc boundaries.
    Sampled curvature uses the signed circumcircle estimator. The curvature
    energy is a trapezoidal integral of kappa**2 at interior vertices,
    using zero curvature at endpoints. Sampling-dependent, diagnostic only.
    """
    xy = tuple(_xy(p) for p in points)
    if len(xy) < 2:
        raise ValueError('at least two points are required')
    if not all(math.isfinite(v) for p in xy for v in p):
        raise ValueError('coordinates must be finite')
    seg = [math.dist(a, b) for a, b in zip(xy, xy[1:])]
    if any(d <= 0 for d in seg):
        raise ValueError('duplicate consecutive points are not allowed')
    jumps = tuple(float(j) for j in curvature_jumps)
    if not all(math.isfinite(j) for j in jumps):
        raise ValueError('curvature jumps must be finite')
    k = [0.0] * len(xy)
    for i in range(1, len(xy)-1):
        ax, ay = xy[i-1]
        bx, by = xy[i]
        cx, cy = xy[i+1]
        cross = (bx-ax)*(cy-ay) - (by-ay)*(cx-ax)
        chord = math.dist(xy[i-1], xy[i+1])
        if chord <= 1e-15:
            raise ValueError('degenerate reversing segment')
        k[i] = 2.0 * cross / (seg[i-1] * seg[i] * chord)
    length = sum(seg)
    # Assign each vertex a dual-cell length: half of each neighboring segment.
    weights = [0.5*seg[0]] + [0.5*(seg[i-1]+seg[i]) for i in range(1, len(xy)-1)] + [0.5*seg[-1]]
    energy = sum(w * value * value for w, value in zip(weights, k))
    maxk = max(abs(value) for value in k)
    maxdelta = max(abs(b-a) for a, b in zip(k, k[1:]))
    return RouteQuality(length, maxk, 1/maxk if maxk > 0 else math.inf,
                        energy, maxdelta, max((abs(j) for j in jumps), default=0.0), len(xy))
