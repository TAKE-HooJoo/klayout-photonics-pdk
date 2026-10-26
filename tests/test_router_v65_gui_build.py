"""Standard-library checks for the generated KLayout macro; no GUI required."""
import ast
import pathlib
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_router_v65_gui import build

class TestGUIBuild(unittest.TestCase):
    def test_generator_source_compiles(self):
        ast.parse((ROOT / 'tools/build_router_v65_gui.py').read_text())

    def test_generated_macro(self):
        source = ROOT / 'pymacros/photonics_router_v6_4.lym'
        if not source.exists():
            self.skipTest('Run this test from repository root after unpacking')
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            dest = pathlib.Path(tmp) / 'router_v65.lym'
            old = source.read_bytes()
            build(source, dest)
            self.assertEqual(source.read_bytes(), old)
            root = ET.parse(dest).getroot()
            self.assertEqual(root.findtext('version'), '6.5')
            body = root.findtext('text')
            ast.parse(body)
            for mode in ('AUTO', 'CSC', 'EULER'):
                self.assertIn("HybridRouterFactory('%s'" % mode, body)
            self.assertIn('route_between_ports_hybrid(', body)
            self.assertIn('_v65_active_router is not self', body)
            self.assertIn('_v65_active_router = self', body)
            self.assertNotIn('if prio:\n            return False', body)
            for marker in ('[v6.5 ACTIVATED]', '[v6.5 DEACTIVATED]',
                           '[v6.5 CLICK]', '[v6.5 ROUTE]', '[v6.5 RESULT]'):
                self.assertIn(marker, body)
            self.assertNotIn('route_between_ports_v64(', body)

if __name__ == '__main__':
    unittest.main()
