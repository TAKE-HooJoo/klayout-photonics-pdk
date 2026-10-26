import unittest
from photonics.routing.hybrid_route_selector import select_route


class TestHybridRouteSelector(unittest.TestCase):
    def setUp(self):
        self.src = (0.0, 0.0)
        self.dst = (40.0, 40.0)

    def route(self, **kw):
        return select_route(self.src, self.dst, 0, 90, **kw)

    def test_euler_success(self):
        result = self.route(mode='EULER')
        self.assertTrue(result.valid)
        self.assertEqual(result.mode, 'EULER')
        self.assertAlmostEqual(result.points[-1][0], 40, places=6)

    def test_auto_prefers_euler(self):
        def must_not_call(*args):
            self.fail('CSC should not be called')
        self.assertEqual(self.route(csc_router=must_not_call).mode, 'EULER')

    def test_auto_falls_back_on_euler_collision(self):
        # Block Euler path but allow simple CSC test path.
        csc_points = (self.src, (40, 0), self.dst)
        def csc(*args):
            return {'valid': True, 'points': csc_points}
        def clear(points):
            return tuple(points) == csc_points
        result = self.route(csc_router=csc, clearance_check=clear)
        self.assertTrue(result.valid)
        self.assertEqual(result.mode, 'CSC')
        self.assertEqual(result.attempts[0], ('EULER', 'OBSTACLE_COLLISION'))

    def test_euler_collision_fails_closed(self):
        result = self.route(mode='EULER', clearance_check=lambda p: False)
        self.assertFalse(result.valid)
        self.assertEqual(result.points, ())

    def test_csc_only(self):
        result = self.route(mode='CSC', csc_router=lambda *a: {'valid': True, 'points': (self.src, self.dst)})
        self.assertTrue(result.valid)
        self.assertEqual(result.mode, 'CSC')

    def test_missing_csc_fails_closed(self):
        result = self.route(mode='CSC')
        self.assertFalse(result.valid)
        self.assertEqual(result.attempts, (('CSC', 'CSC_ROUTER_NOT_CONFIGURED'),))

    def test_bad_csc_endpoint_rejected(self):
        result = self.route(mode='CSC', csc_router=lambda *a: {'valid': True, 'points': ((1, 0), self.dst)})
        self.assertFalse(result.valid)
        self.assertEqual(result.attempts[0][1], 'ENDPOINT_MISMATCH')

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            self.route(mode='OTHER')

    def test_unsupported_euler_fails_closed(self):
        result = select_route(self.src, self.dst, 0, 45, mode='EULER')
        self.assertFalse(result.valid)
        self.assertEqual(result.attempts[0][1], 'UNSUPPORTED_TURN_ANGLE')


if __name__ == '__main__':
    unittest.main()
