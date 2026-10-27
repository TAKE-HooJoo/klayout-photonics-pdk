"""Pure Python tests: python3 -m unittest discover -s tests -p test_euler_sbend.py -v"""
import math
import unittest
from photonics.routing.euler_sbend import route_euler_sbend as route

class TestEulerSBend(unittest.TestCase):
    def test_upward_offset(self):
        r = route((0, 0), (80, 15), 0, 0)
        self.assertTrue(r.valid, r.reason)
        self.assertLess(r.endpoint_error_um, .01)
        self.assertGreater(r.length_um, 80)
        self.assertGreater(r.bend_angle_deg, 0)

    def test_downward_offset(self):
        r = route((0, 0), (80, -15), 0, 0)
        self.assertTrue(r.valid, r.reason)
        self.assertAlmostEqual(r.points[-1][1], -15, places=3)

    def test_rotated(self):
        r = route((0, 0), (-15, 80), 90, 90)
        self.assertTrue(r.valid, r.reason)

    def test_straight(self):
        r = route((0, 0), (40, 0), 0, 0)
        self.assertTrue(r.valid)
        self.assertEqual(len(r.points), 2)

    def test_heading_mismatch(self):
        self.assertEqual(route((0, 0), (80, 15), 0, 90).reason,
                         'UNSUPPORTED_HEADING_DIFFERENCE')

    def test_insufficient_forward(self):
        self.assertEqual(route((0, 0), (2, 15), 0, 0).reason,
                         'INSUFFICIENT_FORWARD_SPACE')

    def test_behind(self):
        self.assertEqual(route((0, 0), (-10, 5), 0, 0).reason,
                         'DESTINATION_BEHIND_SOURCE')

    def test_zero_offset_behind(self):
        self.assertFalse(route((0, 0), (-10, 0), 0, 0).valid)

if __name__ == '__main__':
    unittest.main()
