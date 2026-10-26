import math
import unittest
from photonics.routing.euler_bend import symmetric_euler_bend


class TestEulerBend(unittest.TestCase):
    def test_endpoints_and_heading(self):
        p = symmetric_euler_bend(90, 5, 401)
        self.assertAlmostEqual(p[0].theta, 0)
        self.assertAlmostEqual(p[-1].theta, math.pi / 2)
        self.assertGreater(p[-1].x, 0)
        self.assertGreater(p[-1].y, 0)

    def test_zero_curvature_at_ends(self):
        p = symmetric_euler_bend(90, 5, 401)
        self.assertAlmostEqual(p[0].curvature, 0)
        self.assertAlmostEqual(p[-1].curvature, 0)
        self.assertAlmostEqual(max(q.curvature for q in p), 0.2)

    def test_length_and_radius(self):
        p = symmetric_euler_bend(90, 6.25, 401)
        self.assertAlmostEqual(p[-1].s, math.pi * 6.25)
        self.assertLessEqual(max(abs(q.curvature) for q in p), 1/6.25 + 1e-12)

    def test_right_bend(self):
        p = symmetric_euler_bend(-90, 5, 401)
        self.assertAlmostEqual(p[-1].theta, -math.pi/2)
        self.assertLess(p[-1].y, 0)
        self.assertLess(min(q.curvature for q in p), 0)

    def test_curvature_ramp(self):
        p = symmetric_euler_bend(90, 5, 401)
        self.assertTrue(all(p[i].curvature <= p[i+1].curvature + 1e-12 for i in range(200)))
        self.assertTrue(all(p[i].curvature >= p[i+1].curvature - 1e-12 for i in range(200,400)))

    def test_invalid_parameters(self):
        for kwargs in ({'angle_deg': 0}, {'angle_deg': 180}, {'min_radius_um': 0}, {'samples': 2}):
            with self.assertRaises(ValueError):
                symmetric_euler_bend(**kwargs)

    def test_sampled_tangent_agrees(self):
        p = symmetric_euler_bend(90, 5, 1001)
        for i in (50, 250, 500, 750, 950):
            angle = math.atan2(p[i+1].y-p[i-1].y, p[i+1].x-p[i-1].x)
            self.assertLess(abs(angle-p[i].theta), 0.001)


if __name__ == '__main__':
    unittest.main()
