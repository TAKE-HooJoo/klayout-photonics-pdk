import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.live_shadow_quality_v2 import shadow_scores,candidate_metrics
class Tests(unittest.TestCase):
    def test_empty(self): self.assertEqual(shadow_scores([]),[])
    def test_invalid(self):
        with self.assertRaises(ValueError): shadow_scores([{'length_um':1,'window_energy_inv_um':0,'window_gradient_inv_um2':0,'jump_inv_um':0}],(-1,1,1,1))
    def test_switch(self):
        a=dict(variant='EULER_SBEND',length_um=1.1,window_energy_inv_um=1,window_gradient_inv_um2=.2,jump_inv_um=0)
        b=dict(variant='LSR',length_um=1,window_energy_inv_um=.1,window_gradient_inv_um2=1,jump_inv_um=.128)
        self.assertEqual(shadow_scores([a,b],(1,1,1,0))[0]['variant'],'LSR')
        self.assertEqual(shadow_scores([a,b],(1,1,1,2))[0]['variant'],'EULER_SBEND')
    def test_csc_jump(self):
        class P:
            def __init__(self,x,y):self.x=x;self.y=y
        pts=[P(i,float(i*i)/100) for i in range(200)]
        r=candidate_metrics(pts,'RSL',7.8125)
        self.assertAlmostEqual(r['jump_inv_um'],.128)
if __name__=='__main__':unittest.main(verbosity=2)
