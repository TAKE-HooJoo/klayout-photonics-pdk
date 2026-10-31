"""Synthetic checks for Phase 3E-7.8D-8."""
import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'tools'))
from audit_route_geometry import three_point_curvature, quantile, analyze

assert abs(three_point_curvature((1,0),(0,1),(-1,0))-1)<1e-12
assert abs(three_point_curvature((0,0),(1,0),(2,0)))<1e-12
assert quantile([1,2,3,4,5],0.95)==4.8
r=8.0
arc=[(r*math.cos(i*math.pi/100),r*math.sin(i*math.pi/100)) for i in range(51)]
a=analyze(arc,r,step=0.1,half_window=0.5)
assert a['arc_samples']>20, a
assert abs(a['inferred_arc_radius_um']-r)<0.001, a
assert a['gradient_p95_inv_um2']<0.02, a
print('Phase 3E-7.8D-8 synthetic tests: PASS')
