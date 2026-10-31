import os,sys,math,unittest
sys.path.insert(0,os.path.abspath(os.getcwd()))
from tools.phase3e78d19_csc_match import analytic_metrics,max_point_error
class P:
    def __init__(self,x,y):self.x=x;self.y=y
class Tests(unittest.TestCase):
    def test_quarter(self):
        m=analytic_metrics(10,math.pi/2,0,0)
        self.assertAlmostEqual(m['analytic_energy_inv_um'],math.pi/20)
    def test_two_arcs(self):
        m=analytic_metrics(5,.3,10,.2)
        self.assertAlmostEqual(m['analytic_length_um'],52.5)
    def test_straight(self):
        self.assertEqual(analytic_metrics(5,0,10,0)['analytic_energy_inv_um'],0)
    def test_radius(self):
        self.assertAlmostEqual(analytic_metrics(7.8125,.1,1,.2)['ideal_jump_inv_um'],.128)
    def test_invalid(self):
        with self.assertRaises(ValueError):analytic_metrics(-1,.2,1,.2)
    def test_point_match(self):
        self.assertEqual(max_point_error([P(0,0),P(1,0)],[P(0,0),P(1,0)]),0)
        self.assertEqual(max_point_error([P(0,0)],[P(0,0),P(1,0)]),math.inf)
if __name__=='__main__':unittest.main(verbosity=2)
