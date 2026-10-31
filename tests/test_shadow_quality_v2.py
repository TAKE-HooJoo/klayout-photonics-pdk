#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from shadow_quality_v2 import evaluate, crossover

def row(case, variant, wj, l, e, g, j, winner):
    score=l+e+g+wj*j
    return dict(case=case,variant=variant,weight_length='1',weight_energy='1',weight_gradient='1',weight_jump=str(wj),normalized_length=str(l),normalized_energy=str(e),normalized_gradient=str(g),normalized_jump=str(j),experimental_score=str(score),winner=winner)

class ShadowTests(unittest.TestCase):
    def test_crossover(self):
        rows=[row('baseline_80_15','EULER_SBEND',0,1.0720372350623697,1,.21188717635340495,0,'LSR'),row('baseline_80_15','LSR',0,1,.0376756853502234,1,1,'LSR')]
        self.assertAlmostEqual(crossover(rows),.2462487260655512,places=8)
    def test_switch(self):
        for wj,winner in [(0,'LSR'),(.1,'LSR'),(.25,'EULER_SBEND'),(1,'EULER_SBEND')]:
            rows=[row('baseline_80_15','EULER_SBEND',wj,1.0720372350623697,1,.21188717635340495,0,winner),row('baseline_80_15','LSR',wj,1,.0376756853502234,1,1,winner)]
            self.assertEqual(evaluate(rows)[0]['shadow_winner'],winner)
    def test_single_candidate(self):
        self.assertEqual(evaluate([row('offset_120_25','LSR',1,1,1,1,1,'LSR')])[0]['candidate_count'],1)
    def test_mismatch_rejected(self):
        r=row('x','LSR',1,1,1,1,1,'LSR');r['experimental_score']='1'
        with self.assertRaises(ValueError):evaluate([r])
    def test_winner_mismatch_rejected(self):
        with self.assertRaises(ValueError):evaluate([row('x','LSR',1,1,1,1,1,'EULER_SBEND')])
if __name__=='__main__':unittest.main(verbosity=2)
