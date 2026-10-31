"""Phase 3E-7.8D-5: fixed physical-window curvature diagnostics.

Uses exported polylines, not analytic curves. No Router modification.
"""
import argparse
import bisect
import csv
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IN = ROOT / 'tests/phase3e78d4_output/route_centerlines.csv'
DEFAULT_OUT = ROOT / 'tests/phase3e78d5_output'


def prepare(points):
    if len(points) < 3:
        raise ValueError('need at least three points')
    s = [0.0]
    for a, b in zip(points, points[1:]):
        d = math.dist(a, b)
        if d <= 1e-12:
            raise ValueError('duplicate points')
        s.append(s[-1] + d)
    return s


def point_at(points, s, distance):
    distance = max(0., min(s[-1], distance))
    i = max(0, min(len(s)-2, bisect.bisect_right(s, distance)-1))
    t = (distance-s[i])/(s[i+1]-s[i])
    return (points[i][0]*(1-t)+points[i+1][0]*t,
            points[i][1]*(1-t)+points[i+1][1]*t)


def signed_angle(a, b):
    return math.atan2(a[0]*b[1]-a[1]*b[0], a[0]*b[0]+a[1]*b[1])


def window_curvature(points, s, center, half_window):
    """Turning angle of two chords over fixed 2h physical arc-length support.

    This is a filtered curvature proxy, not pointwise curvature.
    """
    p = point_at(points, s, center-half_window)
    q = point_at(points, s, center)
    r = point_at(points, s, center+half_window)
    u, v = (q[0]-p[0], q[1]-p[1]), (r[0]-q[0], r[1]-q[1])
    if math.hypot(*u) < 1e-12 or math.hypot(*v) < 1e-12:
        return float('nan')
    return signed_angle(u, v)/half_window


def evaluate(points, step, half_window):
    s = prepare(points)
    length = s[-1]
    if half_window <= 0 or step <= 0 or length <= 2*half_window:
        raise ValueError('invalid step/window or route too short')
    # Exclude endpoints: both sides of every evaluation point must have full support.
    n = max(1, math.ceil((length-2*half_window)/step))
    ds = (length-2*half_window)/n
    ks = [window_curvature(points, s, half_window+i*ds, half_window) for i in range(n+1)]
    if not all(math.isfinite(k) for k in ks):
        raise ValueError('degenerate window chord')
    energy = ds*(sum(k*k for k in ks[1:-1])+0.5*(ks[0]**2+ks[-1]**2))
    # Delta is sampling-dependent; gradient is normalized by distance.
    delta = max((abs(b-a) for a,b in zip(ks, ks[1:])), default=0.)
    gradient = delta/ds if ds else 0.
    return dict(length_um=length, actual_step_um=ds, half_window_um=half_window,
                window_energy_inv_um=energy, max_delta_kappa_inv_um=delta,
                max_gradient_inv_um2=gradient, max_abs_kappa_inv_um=max(map(abs,ks)),
                evaluation_points=len(ks))


def load(path):
    grouped = defaultdict(list)
    with path.open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            key = (row['case'], row['mode'], row['variant'], row['designed_radius_um'])
            grouped[key].append((int(row['index']), (float(row['x_um']),float(row['y_um']))))
    return {key:[p for _,p in sorted(rows)] for key,rows in grouped.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=DEFAULT_IN)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--half-window', type=float, default=1.0)
    parser.add_argument('--steps', type=float, nargs='+', default=[0.5,0.25,0.1,0.05])
    args = parser.parse_args()
    if not args.input.exists():
        parser.error('missing input CSV: %s; run KLayout D-4 export first' % args.input)
    args.output.mkdir(parents=True, exist_ok=True)
    output=[]
    for key,points in sorted(load(args.input).items()):
        for step in args.steps:
            result=evaluate(points, step, args.half_window)
            row=dict(zip(('case','mode','variant','designed_radius_um'),key))
            row.update(requested_step_um=step, **result)
            output.append(row)
            print('%-17s %-12s %-12s ds=%5.2f Ew=%9.6f dK=%9.6f' %
                  (key[0],key[1],key[2],step,result['window_energy_inv_um'],result['max_delta_kappa_inv_um']))
    path=args.output/'curvature_window_sweep.csv'
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(output[0]))
        writer.writeheader(); writer.writerows(output)
    print('CSV:',path)
    print('Phase 3E-7.8D-5 window analysis: PASS')

if __name__=='__main__':
    main()
