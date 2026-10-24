"""Standalone static checks: python3 -m unittest discover -s tests -p 'test_router_v63_macro.py' -v"""
import os
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(os.getcwd())

class TestRouterV63Macro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        macro = ROOT / 'pymacros/photonics_router_v6_3.lym'
        cls.code = ET.parse(macro).getroot().findtext('text')

    def test_compiles(self):
        compile(self.code, 'photonics_router_v6_3.lym', 'exec')

    def test_unique_plugin_id(self):
        self.assertIn("'photonics_router_v6_3'", self.code)
        self.assertNotIn("self.register(-1000, 'photonics_router_v6_2'", self.code)

    def test_uses_new_adapter(self):
        self.assertIn('from photonics.integration.router_v62 import route_between_ports', self.code)
        self.assertIn('result = route_between_ports(', self.code)

    def test_preserves_port_discovery(self):
        self.assertIn('def nearest_port(', self.code)
        self.assertIn('def collect_ports(', self.code)

if __name__ == '__main__':
    unittest.main()
