"""Independent phase 16 curvature diagnostics; does not change production scoring.

Polyline finite differences are not an analytic/GDS G2 proof.
"""
import math
from bisect import bisect_right


def prepare(points):
    xy = [(float(p.x), float(p.y)) for p in points]
    if len(xy) < 3:
        raise ValueError('need at least three points')
    clean = [xy[0]]
    arclen = [0.0]
    for p in xy[1:]:
        d = math.dist(clean[-1], p)
        if d > 1e-10:
            clean.append(p)
            arclen.append(arclen[-1] + d)
    if len(clean) < 3 or arclen[-1] <= 0:
        raise ValueError('degenerate polyline')
    return clean, arclen


def position_at(clean, arc, s):
    s = max(0., min(arc[-1], float(s)))
    j = min(len(arc)-2, max(0, bisect_right(arc, s)-1))
    t = (s-arc[j])/(arc[j+1]-arc[j])
    return (clean[j][0]*(1-t)+clean[j+1][0]*t,
            clean[j][1]*(1-t)+clean[j+1][1]*t)


def unwrap(angles):
    out = [angles[0]]
    for a in angles[1:]:
        out.append(out[-1] + (a-out[-1]+math.pi)%(2*math.pi)-math.pi)
    return out


def physical_grid_metrics(points, sample_ds=0.05, tangent_span=1.0,
                          derivative_span=1.0, margin=None):
    """Physical-length symmetric secants and fixed physical derivative span.

    This is a diagnostic of a polygonal centerline. The spans do not shrink
    with sample_ds. Boundary samples are excluded to avoid clipped secants.
    """
    if any(not math.isfinite(v) or v <= 0 for v in
           (sample_ds, tangent_span, derivative_span)):
        raise ValueError('all sampling/spans must be positive finite')
    clean, arc = prepare(points)
    length = arc[-1]
    half_t = tangent_span / 2
    half_d = derivative_span / 2
    edge = max(half_t + half_d, float(margin) if margin is not None else 0.)
    if length <= 2*edge + sample_ds:
        raise ValueError('insufficient centerline for requested physical spans')
    n = math.ceil(length / sample_ds)
    h = length/n
    def heading(s):
        a = position_at(clean,arc,s-half_t)
        b = position_at(clean,arc,s+half_t)
        return math.atan2(b[1]-a[1],b[0]-a[0])
    # Compute heading at s +/- half_d, then difference over fixed distance.
    # This avoids derivative denominator shrinking with sample_ds.
    samples = []
    for i in range(n+1):
        s = i*h
        if s < edge or s > length-edge:
            continue
        a,b = heading(s-half_d), heading(s+half_d)
        k = ((b-a+math.pi)%(2*math.pi)-math.pi)/derivative_span
        samples.append((s,k))
    if len(samples) < 3:
        raise ValueError('insufficient interior samples')
    energy = sum((samples[i][0]-samples[i-1][0]) *
                 (samples[i][1]**2+samples[i-1][1]**2)/2
                 for i in range(1,len(samples)))
    # Fixed physical distance gradient of curvature estimates, using
    # interpolation on the interior sample grid (no extrapolation).
    ss = [s for s,_ in samples]
    ks = [k for _,k in samples]
    def ki(s):
        j = min(len(ss)-2, max(0,bisect_right(ss,s)-1))
        t = (s-ss[j])/(ss[j+1]-ss[j])
        return ks[j]*(1-t)+ks[j+1]*t
    gradients = [abs(ki(s+half_d)-ki(s-half_d))/derivative_span
                 for s in ss if s-half_d >= ss[0] and s+half_d <= ss[-1]]
    return {'length_um':length, 'energy_inv_um':energy,
            'gradient_inv_um2':max(gradients) if gradients else float('nan'),
            'sample_count':len(samples), 'actual_ds_um':h,
            'interior_start_um':ss[0], 'interior_end_um':ss[-1]}


def ideal_csc_jump(variant, radius):
    if variant not in ('LSL','LSR','RSL','RSR'):
        if variant in ('EULER','EULER_SBEND'):
            return 0.0
        raise ValueError('unknown variant')
    if not math.isfinite(radius) or radius <= 0:
        raise ValueError('invalid radius')
    return 1.0/radius


def relative_range(values):
    if not values or any(not math.isfinite(v) for v in values):
        return float('nan')
    denom=max(abs(v) for v in values)
    return (max(values)-min(values))/denom if denom else 0.
