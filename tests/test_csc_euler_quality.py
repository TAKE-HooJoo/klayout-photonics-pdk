#!/usr/bin/env python3
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_csc_euler_quality import ideal_csc_junctions, normalized_scores

class AuditTests(unittest.TestCase):
    def test_lsr_junctions(self):
        js = ideal_csc_junctions(7.8125, 'LSR')
        self.assertEqual(len(js), 2)
        self.assertEqual([j['heading_jump_deg'] for j in js], [0.0, 0.0])
        self.assertTrue(all(math.isclose(j['abs_jump_inv_um'], 0.128) for j in js))
        self.assertGreater(js[0]['curvature_left_inv_um'], 0)
        self.assertLess(js[1]['curvature_right_inv_um'], 0)

    def test_invalid_radius(self):
        with self.assertRaises(ValueError):
            ideal_csc_junctions(0)

    def test_normalization(self):
        a = {'length_um': '87.27574', 'window_energy_inv_um': '.2503067',
             'window_gradient_inv_um2': '.026502', 'jump_inv_um': '0'}
        b = {'length_um': '81.41111', 'window_energy_inv_um': '.0094305',
             'window_gradient_inv_um2': '.125076', 'jump_inv_um': '.128'}
        scores = normalized_scores([a,b], (1,1,1,1))
        self.assertLess(scores[0][1], scores[1][1])
        nojump = normalized_scores([a,b], (1,1,1,0))
        self.assertLess(nojump[1][1], nojump[0][1])

    def test_bad_weight(self):
        with self.assertRaises(ValueError):
            normalized_scores([{'length_um': '1', 'window_energy_inv_um': '0',
                                'window_gradient_inv_um2': '0', 'jump_inv_um': '0'}], (1,-1,1,1))

if __name__ == '__main__':
    unittest.main(verbosity=2)
