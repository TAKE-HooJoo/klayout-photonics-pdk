import unittest,sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.phase3e78d17_csc_audit import turning_proxy,compare_energy
class P:
    def __init__(self,x,y):self.x=x;self.y=y
class Tests(unittest.TestCase):
    def test_quarter_circle(self):
        r=10.0
        pts=[P(r*math.cos(i*math.pi/200),r*math.sin(i*math.pi/200)) for i in range(101)]
        p=turning_proxy(pts,r)
        self.assertAlmostEqual(p['turning_angle_abs_rad'],math.pi/2-math.pi/200,places=9)
    def test_mirror(self):
        pts=[P(0,0),P(1,0),P(2,1),P(3,1)]
        a=turning_proxy(pts,5)
        b=turning_proxy([P(p.x,-p.y) for p in pts],5)
        self.assertAlmostEqual(a['ideal_energy_proxy_inv_um'],b['ideal_energy_proxy_inv_um'])
    def test_straight(self):
        self.assertAlmostEqual(turning_proxy([P(0,0),P(1,0),P(2,0)],5)['ideal_energy_proxy_inv_um'],0)
    def test_invalid_radius(self):
        with self.assertRaises(ValueError):turning_proxy([P(0,0),P(1,0),P(2,1)],0)
    def test_invalid_points(self):
        with self.assertRaises(ValueError):turning_proxy([P(0,0)],5)
    def test_comparison(self):
        self.assertAlmostEqual(compare_energy(.8,1.)['energy_relative_delta'],-.2)
if __name__=='__main__':unittest.main(verbosity=2)
