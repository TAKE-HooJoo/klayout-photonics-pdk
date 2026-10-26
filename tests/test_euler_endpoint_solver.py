import math
import unittest
from photonics.routing.euler_endpoint_solver import route_straight_euler_straight as solve


class TestEulerEndpointSolver(unittest.TestCase):
    def test_left_turn(self):
        r = solve((0, 0), (30, 30), 0, 90)
        self.assertTrue(r.valid, r.reason)
        self.assertAlmostEqual(r.points[0][0], 0)
        self.assertAlmostEqual(r.points[-1][0], 30, places=7)
        self.assertAlmostEqual(r.points[-1][1], 30, places=7)
        self.assertGreater(r.source_lead_um, 0)
        self.assertGreater(r.destination_lead_um, 0)

    def test_right_turn(self):
        r = solve((0, 0), (30, -30), 0, -90)
        self.assertTrue(r.valid, r.reason)
        self.assertAlmostEqual(r.points[-1][1], -30, places=7)

    def test_rotated_turn(self):
        r = solve((5, 8), (-25, 38), 90, 180)
        self.assertTrue(r.valid, r.reason)
        self.assertLess(r.endpoint_error_um, 1e-7)

    def test_insufficient_space(self):
        r = solve((0, 0), (6.25, 6.25), 0, 90)
        self.assertFalse(r.valid)
        self.assertEqual(r.reason, 'INSUFFICIENT_LEAD_SPACE')
        self.assertEqual(r.points, ())

    def test_unsupported_turn(self):
        r = solve((0, 0), (30, 30), 0, 45)
        self.assertFalse(r.valid)
        self.assertEqual(r.reason, 'UNSUPPORTED_TURN_ANGLE')

    def test_radius_constraint(self):
        r = solve((0, 0), (30, 30), 0, 90, min_radius_um=6.25)
        self.assertTrue(r.valid)
        self.assertAlmostEqual(r.min_radius_um, 6.25)
        self.assertGreater(r.length_um, math.pi * 6.25)

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            solve((0, 0), (30, 30), 0, 90, min_radius_um=-1)


if __name__ == '__main__':
    unittest.main()
