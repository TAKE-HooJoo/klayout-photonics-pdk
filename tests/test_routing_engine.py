import math
import unittest
from photonics.circuit.geometry import Point
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.routing import RoutingEngine

class TestRoutingEngine(unittest.TestCase):
    def setUp(self):
        self.xs=WaveguideCrossSection('strip',.5,5.)
        self.rules=DesignRules(.4,.5,5.)
        self.engine=RoutingEngine(self.xs,self.rules)

    def test_straight(self):
        r=self.engine.route(Point(0,0),Point(30,0),(1,0),(-1,0))
        self.assertTrue(r.valid)
        self.assertEqual(r.variant,'STRAIGHT')
        self.assertAlmostEqual(r.length_um,30.)

    def test_s_bend(self):
        r=self.engine.route(Point(0,0),Point(50,15),(1,0),(-1,0))
        self.assertTrue(r.valid,r.reason)
        self.assertLessEqual(r.tangent_error_source_deg,5.)
        self.assertLessEqual(r.tangent_error_destination_deg,5.)

    def test_incompatible_directions(self):
        r=self.engine.route(Point(0,0),Point(30,20),(0,1),(-1,0))
        self.assertIsInstance(r.valid,bool)
        if r.valid:
            self.assertLessEqual(max(r.tangent_error_source_deg,r.tangent_error_destination_deg),5.)

    def test_rules_reject_narrow_waveguide(self):
        with self.assertRaises(ValueError):
            RoutingEngine(WaveguideCrossSection('narrow',.3,5.),self.rules)

    def test_coincident_ports(self):
        r=self.engine.route(Point(0,0),Point(0,0),(1,0),(-1,0))
        self.assertFalse(r.valid)
        self.assertEqual(r.reason,'COINCIDENT_PORTS')

if __name__=='__main__': unittest.main()
