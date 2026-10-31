import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_production_shadow_v2 import compare
class ComparisonTests(unittest.TestCase):
    def test_matching_and_missing_reference(self):
        p=[dict(case='baseline_80_15',mode='AUTO_QUALITY',valid='True',variant='LSR',reason='',length_um='81',shape_delta='1',point_count='74'),dict(case='negative_80_-15',mode='AUTO_QUALITY',valid='True',variant='EULER_SBEND',reason='',length_um='87',shape_delta='1',point_count='403')]
        s=[dict(case='baseline_80_15',weight_jump='1',shadow_winner='LSR')]
        out=compare(p,s)
        self.assertEqual(out[0]['match'],'True')
        self.assertEqual(out[1]['match'],'NOT_COMPARABLE')
    def test_mismatch_is_recorded_not_failure(self):
        p=[dict(case='baseline_80_15',mode='AUTO_QUALITY',valid='True',variant='LSR',reason='',length_um='81',shape_delta='1',point_count='74')]
        s=[dict(case='baseline_80_15',weight_jump='1',shadow_winner='EULER_SBEND')]
        self.assertEqual(compare(p,s)[0]['match'],'False')
    def test_no_auto_quality_rejected(self):
        with self.assertRaises(ValueError): compare([dict(mode='CSC')],[])
if __name__=='__main__':unittest.main(verbosity=2)
