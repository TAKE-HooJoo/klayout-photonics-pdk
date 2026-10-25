import math
import unittest
from photonics.routing.route_quality import analyze_route


class TestRouteQuality(unittest.TestCase):
    def test_straight(self):
        r=analyze_route([(0,0),(5,0),(10,0)])
        self.assertEqual(r.length_um,10)
        self.assertEqual(r.max_turn_deg,0)
        self.assertTrue(math.isinf(r.min_sampled_radius_um))
        self.assertFalse(r.radius_violations)

    def test_right_angle(self):
        r=analyze_route([(0,0),(5,0),(5,5)])
        self.assertAlmostEqual(r.max_turn_deg,90)
        self.assertEqual(len(r.sharp_vertices),1)
        self.assertEqual(len(r.radius_violations),1)

    def test_circle_samples(self):
        radius=10.0
        pts=[(radius*math.cos(i*0.05),radius*math.sin(i*0.05)) for i in range(21)]
        r=analyze_route(pts,min_radius_um=5)
        self.assertAlmostEqual(r.min_sampled_radius_um,radius,places=6)
        self.assertFalse(r.radius_violations)

    def test_duplicate(self):
        r=analyze_route([(0,0),(0,0),(1,0)])
        self.assertEqual(r.zero_length_segments,(0,))

    def test_two_points(self):
        r=analyze_route([(0,0),(3,4)])
        self.assertEqual(r.length_um,5)
        self.assertTrue(math.isinf(r.min_sampled_radius_um))


if __name__=='__main__':
    unittest.main()
