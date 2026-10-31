"""Phase 3E-7.8D-9: sampled geometry diagnostics; NOT analytic G2 proof."""
import argparse
import csv
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from analyze_curvature_window import load, prepare
from audit_route_geometry import three_point_curvature

CSC = {'LSR','RSL','LSL','RSR','LRL','RLR'}

def analyze(points, radius, threshold=0.25):
    if radius <= 0 or not 0 < threshold < 1:
        raise ValueError('invalid radius/threshold')
    s = prepare(points)
    target = 1/radius
    curvature = [three_point_curvature(points[i-1], points[i], points[i+1]) for i in range(1,len(points)-1)]
    values = [abs(k) for k in curvature if k is not None and math.isfinite(k)]
    if not values: raise ValueError('no usable curvature samples')
    # Turning angle at each original polyline vertex (not analytic junction angle).
    angles=[]
    for i in range(1,len(points)-1):
        a=(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1])
        b=(points[i+1][0]-points[i][0],points[i+1][1]-points[i][1])
        angles.append(abs(math.degrees(math.atan2(a[0]*b[1]-a[1]*b[0],a[0]*b[0]+a[1]*b[1]))))
    # A curvature estimate is from the source vertices, NOT a continuous curve.
    arc=[v for v in values if (1-threshold)*target <= v <= (1+threshold)*target]
    peak=max(values)
    # Curvature in straight/arc transitions is contaminated by the 3-point stencil.
    transition_count=sum(1 for v in values if threshold*target < v < (1-threshold)*target)
    return dict(length_um=s[-1],points=len(points),target_curvature_inv_um=target,
                max_sampled_abs_curvature_inv_um=peak,
                min_sampled_radius_um=1/peak if peak else None,
                peak_over_target=peak/target,arc_like_samples=len(arc),
                transition_samples=transition_count,
                max_vertex_turn_deg=max(angles),
                sampled_radius_constraint=('PASS_SAMPLED' if peak <= target*(1+0.01) else 'EXCEEDS_SAMPLED'),
                proof_status='POLYLINE_ONLY_NOT_G1_G2_PROOF')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,default=ROOT/'tests/phase3e78d4_output/route_centerlines.csv')
    p.add_argument('--output',type=Path,default=ROOT/'tests/phase3e78d9_output')
    a=p.parse_args()
    if not a.input.exists(): p.error('missing centerline CSV; run D-4 exporter first')
    rows=[]
    for key,points in sorted(load(a.input).items()):
        case,mode,variant,radius_s=key
        m=analyze(points,float(radius_s))
        row=dict(case=case,mode=mode,variant=variant,designed_radius_um=radius_s,**m)
        rows.append(row)
        print('%-17s %-12s %-12s kmax=%.6f Rmin=%.5f turn=%.4f deg status=%s' %
              (case,mode,variant,m['max_sampled_abs_curvature_inv_um'],m['min_sampled_radius_um'],
               m['max_vertex_turn_deg'],m['sampled_radius_constraint']))
    if not rows: p.error('empty input')
    a.output.mkdir(parents=True,exist_ok=True)
    out=a.output/'junction_polyline_audit.csv'
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('CSV:',out)
    print('Phase 3E-7.8D-9: PASS (polyline diagnostic only; analytic G1/G2 remains unverified)')
if __name__=='__main__': main()
