import unittest
from photonics.pdk import LayerMap, WaveguideCrossSection, DesignRules

class PDKModelTests(unittest.TestCase):
    def test_default_layers(self):
        lm = LayerMap()
        self.assertEqual((lm.waveguide.layer, lm.waveguide.datatype), (1, 0))
        self.assertEqual((lm.optical_pin.layer, lm.optical_pin.datatype), (2, 0))

    def test_cross_section(self):
        xs = WaveguideCrossSection('strip', 0.5, 5.0)
        rules = DesignRules(0.4, 0.2, 5.0)
        self.assertTrue(rules.validate_cross_section(xs))
        self.assertFalse(DesignRules(0.6, 0.2, 5.0).validate_cross_section(xs))

    def test_invalid_values(self):
        with self.assertRaises(ValueError):
            WaveguideCrossSection('strip', 0, 5)
        with self.assertRaises(ValueError):
            DesignRules(0.4, -1, 5)

if __name__ == '__main__':
    unittest.main()
