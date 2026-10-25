import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from photonics.circuit.geometry import Point
from photonics.routing.continuity import sharp_corners
from photonics.routing.fillet import fillet_polyline

class ContinuityTest(unittest.TestCase):
    def test_detect_kink(self):
        points = (Point(0, 0), Point(10, 0), Point(20, 10))
        self.assertEqual(len(sharp_corners(points)), 1)
        self.assertAlmostEqual(sharp_corners(points)[0][1], 45)

    def test_fillet_tangent(self):
        pts = fillet_polyline((Point(0, 0), Point(20, 0), Point(40, 20)), 5)
        self.assertFalse(sharp_corners(pts, 5))
        self.assertEqual(pts[0], Point(0, 0))
        self.assertEqual(pts[-1], Point(40, 20))

    def test_insufficient_lead_rejected(self):
        with self.assertRaises(ValueError):
            fillet_polyline((Point(0, 0), Point(1, 0), Point(1, 1)), 5)

if __name__ == '__main__':
    unittest.main()
