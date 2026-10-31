import os
import sys
import unittest
from dataclasses import dataclass
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.audit_live_shadow_convergence import audit_candidates, convergence_report

@dataclass
class P:
    x: float
    y: float

class Tests(unittest.TestCase):
    def setUp(self):
        self.points = tuple(P(float(i), 0.0) for i in range(11))
        self.euler = dict(case='test', variant='EULER_SBEND', points=self.points,
                          designed_radius_um=6.25)
        self.csc = dict(case='test', variant='LSR', points=self.points,
                        designed_radius_um=7.8125)
    def test_sweep_shape(self):
        rows, summary = audit_candidates([self.euler, self.csc], ds_values=(.2,.05))
        self.assertEqual(len(rows),4)
        self.assertEqual(len(summary),2)
        self.assertTrue(all(s['candidate_count']==2 for s in summary))
    def test_ideal_jump(self):
        rows, _ = audit_candidates([self.euler,self.csc], ds_values=(.1,))
        jumps={r['variant']:r['jump_inv_um'] for r in rows}
        self.assertAlmostEqual(jumps['LSR'], .128)
        self.assertEqual(jumps['EULER_SBEND'],0.)
    def test_invalid_ds(self):
        with self.assertRaises(ValueError):
            audit_candidates([self.euler], ds_values=(0.,))
    def test_report(self):
        rows, summary = audit_candidates([self.euler,self.csc], ds_values=(.2,.1))
        report=convergence_report(rows,summary)
        self.assertEqual(len(report),2)
        self.assertTrue(all(r['winner_stable'] for r in report))
    def test_mirror_straight(self):
        mirror=tuple(P(p.x,-p.y) for p in self.points)
        a=dict(self.euler,case='plus')
        b=dict(self.euler,case='minus',points=mirror)
        rows,_=audit_candidates([a,b],ds_values=(.2,.05))
        for ds in (.2,.05):
            x=[r for r in rows if r['case']=='plus' and r['ds_um']==ds][0]
            y=[r for r in rows if r['case']=='minus' and r['ds_um']==ds][0]
            self.assertAlmostEqual(x['window_energy_inv_um'],y['window_energy_inv_um'])
if __name__=='__main__':
    unittest.main(verbosity=2)
