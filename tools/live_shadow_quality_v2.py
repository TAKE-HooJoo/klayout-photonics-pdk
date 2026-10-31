"""Phase 3E-7.8D-14: score exactly the candidates passed to AUTO_QUALITY.

The KLayout runner temporarily wraps the production evaluator; it never changes
candidate generation, acceptance, scoring or placement.
"""
import math

CSC = {'LSL', 'LSR', 'RSL', 'RSR'}

def centerline_metrics(points, ds=0.05, window=1.0):
    """Fixed-window curvature proxy and max |dκ/ds|; NOT optical loss.

    Finite differences on an arc-length-interpolated polyline. This is a
    diagnostic, not an analytic continuity or GDS proof.
    """
    xy = [(float(p.x), float(p.y)) for p in points]
    lengths = [0.0]
    clean = [xy[0]]
    for p in xy[1:]:
        d = math.dist(clean[-1], p)
        if d > 1e-10:
            lengths.append(lengths[-1] + d)
            clean.append(p)
    if len(clean) < 3 or lengths[-1] < 2 * window:
        raise ValueError('insufficient centerline for fixed-window analysis')
    n = max(3, math.ceil(lengths[-1] / ds))
    h = lengths[-1] / n
    res = []
    seg = 0
    for i in range(n+1):
        s = min(lengths[-1], i*h)
        while seg < len(lengths)-2 and lengths[seg+1] < s:
            seg += 1
        t = (s-lengths[seg])/(lengths[seg+1]-lengths[seg])
        res.append((clean[seg][0]*(1-t)+clean[seg+1][0]*t,
                    clean[seg][1]*(1-t)+clean[seg+1][1]*t))
    # Fixed-window tangent directions from symmetric secants.
    half = max(1, round(window / (2*h)))
    headings = []
    for i in range(n+1):
        a, b = max(0,i-half), min(n,i+half)
        headings.append(math.atan2(res[b][1]-res[a][1],res[b][0]-res[a][0]))
    for i in range(1,len(headings)):
        headings[i] = headings[i-1] + (headings[i]-headings[i-1]+math.pi)%(2*math.pi)-math.pi
    curvature = [(headings[min(n,i+1)]-headings[max(0,i-1)]) / ((min(n,i+1)-max(0,i-1))*h) for i in range(n+1)]
    energy = h * (sum(k*k for k in curvature[1:-1]) + .5*(curvature[0]**2+curvature[-1]**2))
    grad = max(abs(curvature[i+1]-curvature[i-1])/(2*h) for i in range(1,n))
    return energy, grad

def candidate_metrics(points, variant, designed_radius_um):
    energy, grad = centerline_metrics(points)
    if variant in CSC:
        radius = float(designed_radius_um)
        if not math.isfinite(radius) or radius <= 0:
            raise ValueError('invalid CSC radius')
        jump = 1.0/radius  # ideal CSC model only
    elif variant in ('EULER_SBEND','EULER'):
        jump = 0.0  # analytic Euler model only
    else:
        raise ValueError('unsupported route variant: '+variant)
    length = sum(math.dist((a.x,a.y),(b.x,b.y)) for a,b in zip(points,points[1:]))
    return dict(length_um=length,window_energy_inv_um=energy,
                window_gradient_inv_um2=grad,jump_inv_um=jump)

def shadow_scores(candidates, weights=(1.,1.,1.,1.)):
    if len(weights)!=4 or any(not math.isfinite(w) or w<0 for w in weights):
        raise ValueError('invalid weights')
    if not candidates:
        return []
    keys=('length_um','window_energy_inv_um','window_gradient_inv_um2','jump_inv_um')
    vals=[[float(c[k]) for k in keys] for c in candidates]
    if any(any(not math.isfinite(v) or v<0 for v in vs) for vs in vals):
        raise ValueError('invalid metrics')
    refs=[min(v[0] for v in vals)] + [max(v[i] for v in vals) for i in range(1,4)]
    if refs[0]<=0: raise ValueError('invalid length')
    result=[]
    for c,vs in zip(candidates,vals):
        norm=[vs[0]/refs[0]]+[vs[i]/refs[i] if refs[i]>0 else 0. for i in range(1,4)]
        result.append(dict(c,shadow_score=sum(a*b for a,b in zip(weights,norm)),
                           normalized_length=norm[0],normalized_energy=norm[1],
                           normalized_gradient=norm[2],normalized_jump=norm[3]))
    return sorted(result,key=lambda r:(r['shadow_score'],r['length_um'],r['variant']))
