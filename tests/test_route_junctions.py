"""Synthetic checks for D-9 polyline geometry diagnostic."""
import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'tools'))
from audit_route_junctions import analyze

def main():
    straight=[(i*0.1,0.) for i in range(101)]
    s=analyze(straight,6.25)
    assert s['max_sampled_abs_curvature_inv_um'] < 1e-10
    assert s['sampled_radius_constraint']=='PASS_SAMPLED'
    radius=7.8125
    arc=[(radius*math.cos(i*math.pi/200),radius*math.sin(i*math.pi/200)) for i in range(101)]
    a=analyze(arc,radius)
    assert abs(a['max_sampled_abs_curvature_inv_um']-1/radius)<1e-8
    assert a['sampled_radius_constraint']=='PASS_SAMPLED'
    try: analyze(straight,-1)
    except ValueError: pass
    else: raise AssertionError('negative radius must fail')
    print('Phase 3E-7.8D-9 synthetic tests: PASS')
if __name__=='__main__': main()
