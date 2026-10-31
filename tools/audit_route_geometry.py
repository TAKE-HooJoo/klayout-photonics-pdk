"""Phase 3E-7.8D-8: polyline geometry audit (diagnostic, not proof of G2)."""
import argparse
import csv
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from analyze_curvature_window import load, prepare, point_at, window_curvature

DEFAULT_IN = ROOT / 'tests/phase3e78d4_output/route_centerlines.csv'
DEFAULT_OUT = ROOT / 'tests/phase3e78d8_output'


def quantile(values, q):
    if not values:
        return None
    v = sorted(values)
    x = (len(v) - 1) * q
    i = int(x)
    return v[i] if i == len(v)-1 else v[i] + (v[i+1]-v[i])*(x-i)


def three_point_curvature(a, b, c):
    ab = math.dist(a,b); bc = math.dist(b,c); ac = math.dist(a,c)
    if min(ab,bc,ac) <= 1e-12:
        return None
    cross = (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    return 2*cross/(ab*bc*ac)


def analyze(points, radius, step=0.1, half_window=1.0):
    s = prepare(points)
    length = s[-1]
    if radius <= 0 or step <= 0 or half_window <= 0 or length <= 2*half_window:
        raise ValueError('invalid radius, step, window or length')
    # Original-vertex circumcircle estimates, with chord-length guards.
    raw = []
    for i in range(1,len(points)-1):
        k = three_point_curvature(points[i-1], points[i], points[i+1])
        if k is not None and math.isfinite(k):
            raw.append(abs(k))
    target = 1/radius
    # Classify only locally circular samples, not tangent-transition samples.
    arc = [k for k in raw if 0.7*target <= k <= 1.3*target]
    arc_median = quantile(arc,0.5)
    # Use a physical window, and only sample positions with complete support.
    n = max(2,math.ceil((length-2*half_window)/step))
    ds = (length-2*half_window)/n
    ks = [window_curvature(points,s,half_window+i*ds,half_window) for i in range(n+1)]
    if not all(math.isfinite(k) for k in ks):
        raise ValueError('nonfinite curvature')
    grads = [(ks[i+1]-ks[i])/ds for i in range(n)]
    abs_grads = list(map(abs,grads))
    # Integral over full-support interior, excluding unsupported end intervals.
    gradient_l2 = sum(g*g for g in grads)*ds
    return dict(length_um=length,original_points=len(points),target_curvature_inv_um=target,
                arc_samples=len(arc),arc_median_curvature_inv_um=arc_median,
                inferred_arc_radius_um=(1/arc_median if arc_median else None),
                arc_radius_rel_error=(abs(1/arc_median-radius)/radius if arc_median else None),
                gradient_p95_inv_um2=quantile(abs_grads,0.95),
                gradient_max_inv_um2=max(abs_grads),
                gradient_l2_inv_um3=gradient_l2,
                step_actual_um=ds,half_window_um=half_window)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,default=DEFAULT_IN)
    ap.add_argument('--output',type=Path,default=DEFAULT_OUT)
    ap.add_argument('--steps',type=float,nargs='+',default=[0.5,0.25,0.1,0.05])
    ap.add_argument('--half-window',type=float,default=1.0)
    args=ap.parse_args()
    if not args.input.exists():
        ap.error('missing centerlines; run klayout -b -r tests/export_route_points_v65.py')
    if any(x<=0 for x in args.steps) or args.half_window<=0:
        ap.error('steps and half-window must be positive')
    rows=[]
    for key,points in sorted(load(args.input).items()):
        case,mode,variant,radius_str=key
        radius=float(radius_str)
        for step in args.steps:
            m=analyze(points,radius,step,args.half_window)
            # Polygonal samples cannot certify G2, nor locate analytic CSC junctions.
            status=('CSC_ARC_ESTIMATE_ONLY' if variant in ('LSR','RSL','LSL','RSR','LRL','RLR')
                    else 'EULER_G2_NOT_PROVEN')
            row=dict(case=case,mode=mode,variant=variant,designed_radius_um=radius,
                     requested_step_um=step,verification_scope=status,**m)
            rows.append(row)
            print('%-17s %-12s %-12s ds=%5.2f P95=%9.6f G2=%9.6f Rarc=%s' %
                  (case,mode,variant,step,m['gradient_p95_inv_um2'],m['gradient_l2_inv_um3'],
                   'N/A' if m['inferred_arc_radius_um'] is None else '%.5f'%m['inferred_arc_radius_um']))
    if not rows:
        ap.error('empty route centerlines')
    args.output.mkdir(parents=True,exist_ok=True)
    out=args.output/'route_geometry_audit.csv'
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('CSV:',out)
    print('Phase 3E-7.8D-8 geometry diagnostic: PASS (G2 and junction geometry not proven)')

if __name__=='__main__':
    main()
