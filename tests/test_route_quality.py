"""Run: python3 -m unittest discover -s tests -p 'test_route_quality.py' -v"""
import math
import unittest
from photonics.routing.route_quality import evaluate_route_quality


class TestRouteQuality(unittest.TestCase):
    def test_straight(self):
        q = evaluate_route_quality([(0, 0), (5, 0), (10, 0)])
        self.assertAlmostEqual(q.length_um, 10)
        self.assertEqual(q.curvature_energy_inv_um, 0)
        self.assertTrue(math.isinf(q.min_sampled_radius_um))

    def test_quarter_circle(self):
        radius = 10
        points = [(radius*math.cos(t*math.pi/2/100), radius*math.sin(t*math.pi/2/100)) for t in range(101)]
        q = evaluate_route_quality(points)
        self.assertAlmostEqual(q.length_um, math.pi*radius/2, places=3)
        self.assertAlmostEqual(q.max_abs_curvature_inv_um, 1/radius, places=5)
        # Endpoint curvature is conventionally zero, so the quadrature is approximate.
        self.assertAlmostEqual(q.curvature_energy_inv_um, math.pi/(2*radius), delta=0.004)

    def test_left_right_sign_invariant_energy(self):
        a = [(0, 0), (1, 0), (2, 1), (3, 2)]
        b = [(x, -y) for x, y in a]
        qa, qb = evaluate_route_quality(a), evaluate_route_quality(b)
        self.assertAlmostEqual(qa.curvature_energy_inv_um, qb.curvature_energy_inv_um)

    def test_declared_jump(self):
        q = evaluate_route_quality([(0, 0), (10, 0)], [0.125, -0.125])
        self.assertAlmostEqual(q.max_declared_jump_inv_um, 0.125)

    def test_invalid(self):
        for points in ([], [(0, 0)], [(0, 0), (0, 0)], [(0, 0), (math.inf, 0)], [(0, 0), (1, 0), (0, 0)]):
            with self.subTest(points=points):
                with self.assertRaises(ValueError):
                    evaluate_route_quality(points)
        with self.assertRaises(ValueError):
            evaluate_route_quality([(0, 0), (1, 0)], [math.nan])


if __name__ == '__main__':
    unittest.main()
