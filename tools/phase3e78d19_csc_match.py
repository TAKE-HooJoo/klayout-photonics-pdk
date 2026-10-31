"""Read-only reconstruction of Dubins CSC parameters; no router monkeypatches."""
import math


def analytic_metrics(radius, t, p, q):
    vals = (radius, t, p, q)
    if not all(math.isfinite(float(v)) for v in vals) or radius <= 0 or min(t, p, q) < 0:
        raise ValueError('Invalid CSC parameters')
    return {'arc1_rad': t, 'arc2_rad': q, 'straight_um': radius*p,
            'analytic_length_um': radius*(t+p+q),
            'analytic_energy_inv_um': (t+q)/radius,
            'ideal_jump_inv_um': 1/radius}


def max_point_error(a, b):
    if len(a) != len(b) or not a:
        return math.inf
    return max(math.hypot(x.x-y.x, x.y-y.y) for x,y in zip(a,b))


def reconstruct_matches(route, start, end, source_outward, destination_outward,
                        radius, samples_per_arc=36, tolerance_um=1e-8):
    """Return exact point-matched Dubins candidate(s), not an inferred approximation.

    This only reconstructs a *direct* CSC segment, not a waypoint composite.
    """
    from photonics.routing.dubins import words, candidate, mod2pi
    from photonics.routing.geometry import unit
    if not route.valid or route.variant not in ('LSL','LSR','RSL','RSR'):
        return []
    src=unit(source_outward); dst=unit(destination_outward)
    arrival=(-dst[0],-dst[1])
    dx=end.x-start.x; dy=end.y-start.y
    D=math.hypot(dx,dy)
    if D < 1e-9 or radius <= 0:
        return []
    theta=math.atan2(dy,dx)
    alpha=mod2pi(math.atan2(src[1],src[0])-theta)
    beta=mod2pi(math.atan2(arrival[1],arrival[0])-theta)
    found=[]
    for word,t,p,q in words(alpha,beta,D/radius):
        if word != route.variant or math.degrees(t+q)>240:
            continue
        points=candidate(start,end,src,arrival,radius,word,t,p,q,samples_per_arc)
        if points is None:
            continue
        error=max_point_error(route.points,points)
        if error <= tolerance_um:
            record={'variant':word,'point_max_error_um':error,
                    'point_count':len(points),'provenance':'EXACT_MATCHED'}
            record.update(analytic_metrics(radius,t,p,q))
            found.append(record)
    return found
