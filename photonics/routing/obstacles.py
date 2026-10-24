"""Pure Python, conservative centreline-versus-rectangular-obstacle screening.

Coordinates and dimensions are in micrometres. Rectangles represent occupied
waveguide geometry; use the KLayout adapter for exact polygon checks later.
"""
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Obstacle:
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    owner: str = ''

    def __post_init__(self):
        if not all(isfinite(v) for v in (self.xmin, self.ymin, self.xmax, self.ymax)):
            raise ValueError('Obstacle coordinates must be finite')
        if self.xmin > self.xmax or self.ymin > self.ymax:
            raise ValueError('Invalid obstacle bounds')


def _segment_intersects_rect(a, b, r):
    """Closed segment intersects closed rectangle (Liang-Barsky clipping)."""
    dx, dy = b.x - a.x, b.y - a.y
    p = (-dx, dx, -dy, dy)
    q = (a.x-r.xmin, r.xmax-a.x, a.y-r.ymin, r.ymax-a.y)
    lo, hi = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return False
        else:
            t = qi / pi
            if pi < 0:
                lo = max(lo, t)
            else:
                hi = min(hi, t)
            if lo > hi:
                return False
    return True


def detect_obstacles(points, width_um, spacing_um, obstacles, ignored_owners=()):
    """Return obstacle indices conservatively overlapping buffered route.

    Rectangles are expanded by width/2 + spacing, using an L-infinity buffer.
    This may report false positives at corners, never silently ignores them.
    Ignored owners are an explicit *whole-object* exemption, not port-local.
    """
    if not isfinite(width_um) or not isfinite(spacing_um) or width_um <= 0 or spacing_um < 0:
        raise ValueError('Invalid width or spacing')
    pts = tuple(points)
    if len(pts) < 2:
        raise ValueError('Route needs at least two points')
    if not all(isfinite(p.x) and isfinite(p.y) for p in pts):
        raise ValueError('Non-finite route coordinates')
    pad = width_um / 2 + spacing_um
    excluded = set(ignored_owners)
    hits = []
    for i, obs in enumerate(obstacles):
        if obs.owner and obs.owner in excluded:
            continue
        expanded = Obstacle(obs.xmin-pad, obs.ymin-pad, obs.xmax+pad, obs.ymax+pad, obs.owner)
        if any(_segment_intersects_rect(a, b, expanded) for a, b in zip(pts, pts[1:])):
            hits.append(i)
    return tuple(hits)
