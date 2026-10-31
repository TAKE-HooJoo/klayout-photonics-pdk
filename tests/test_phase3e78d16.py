import os,sys,unittest,math
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from tools.phase3e78d16_curvature import physical_grid_metrics,ideal_csc_jump,relative_range
class P:
    def __init__(self,x,y):self.x=x;self.y=y
class Tests(unittest.TestCase):
    def test_straight(self):
        m=physical_grid_metrics([P(i,0) for i in range(101)])
        self.assertAlmostEqual(m['energy_inv_um'],0,places=10)
        self.assertAlmostEqual(m['gradient_inv_um2'],0,places=10)
    def test_mirror(self):
        pts=[P(i,5*math.sin(i/30)) for i in range(101)]
        a=physical_grid_metrics(pts)
        b=physical_grid_metrics([P(p.x,-p.y) for p in pts])
        self.assertAlmostEqual(a['energy_inv_um'],b['energy_inv_um'],places=10)
        self.assertAlmostEqual(a['gradient_inv_um2'],b['gradient_inv_um2'],places=10)
    def test_fixed_physical_grid(self):
        pts=[P(i,5*math.sin(i/30)) for i in range(101)]
        a=physical_grid_metrics(pts,sample_ds=.1)
        b=physical_grid_metrics(pts,sample_ds=.025)
        self.assertLess(abs(a['energy_inv_um']-b['energy_inv_um']),.01)
    def test_jump(self):
        self.assertAlmostEqual(ideal_csc_jump('RSL',7.8125),.128)
        self.assertEqual(ideal_csc_jump('EULER_SBEND',6.25),0)
    def test_invalid(self):
        with self.assertRaises(ValueError):physical_grid_metrics([P(0,0),P(1,0),P(2,0)],sample_ds=0)
    def test_range(self):
        self.assertAlmostEqual(relative_range([1,2]),.5)
if __name__=='__main__':unittest.main(verbosity=2)
