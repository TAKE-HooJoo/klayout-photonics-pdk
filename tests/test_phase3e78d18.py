import os,sys,math,unittest
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from tools.phase3e78d18_csc import analytic_csc_energy,parameter_status
class Test(unittest.TestCase):
 def test_quarter(self):
  x=analytic_csc_energy(10,math.pi/2,0,4)
  self.assertAlmostEqual(x['analytic_energy_inv_um'],math.pi/20)
 def test_two_arcs(self):
  x=analytic_csc_energy(8,.2,.3,10)
  self.assertAlmostEqual(x['arc_length_um'],4)
 def test_jump(self): self.assertAlmostEqual(analytic_csc_energy(7.8125,.2,.2,1)['ideal_jump_inv_um'],.128)
 def test_invalid(self):
  with self.assertRaises(ValueError): analytic_csc_energy(0,1,1,1)
 def test_no_guess(self): self.assertIsNone(parameter_status(object()))
 def test_exposed(self):
  class O: arc1_rad=.2;arc2_rad=.3;straight_um=10
  self.assertAlmostEqual(parameter_status(O())['arc2_rad'],.3)
if __name__=='__main__': unittest.main(verbosity=2)
