import unittest
from photonics.circuit.geometry import Point
from photonics.routing.obstacles import Obstacle, detect_obstacles


class TestObstacles(unittest.TestCase):
    def setUp(self):
        self.route = (Point(0, 0), Point(10, 0))

    def test_crossing(self):
        self.assertEqual(detect_obstacles(self.route, .5, .5,
                         (Obstacle(4, -1, 6, 1),)), (0,))

    def test_clear(self):
        self.assertEqual(detect_obstacles(self.route, .5, .5,
                         (Obstacle(4, 2, 6, 3),)), ())

    def test_spacing_violation(self):
        self.assertEqual(detect_obstacles(self.route, .5, .5,
                         (Obstacle(4, .6, 6, 1),)), (0,))

    def test_owner_exemption(self):
        self.assertEqual(detect_obstacles(self.route, .5, .5,
                         (Obstacle(0, -1, 1, 1, 'source'),),
                         ignored_owners=('source',)), ())

    def test_invalid_obstacle(self):
        with self.assertRaises(ValueError):
            Obstacle(2, 0, 1, 1)


if __name__ == '__main__':
    unittest.main()
