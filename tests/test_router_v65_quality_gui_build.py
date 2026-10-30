"""Pure Python tests for AUTO_QUALITY registration in v6.5 GUI generator."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / 'tools' / 'build_router_v65_gui.py'


class TestQualityGUI(unittest.TestCase):
    def test_quality_mode_registered_once(self):
        src = BUILDER.read_text(encoding='utf-8')
        self.assertEqual(src.count("HybridRouterFactory('AUTO_QUALITY',"), 1)
        self.assertIn("'photonics_router_v6_5_auto_quality'", src)

    def test_existing_modes_and_active_owner_preserved(self):
        src = BUILDER.read_text(encoding='utf-8')
        for mode in ('AUTO', 'CSC', 'EULER'):
            self.assertIn("HybridRouterFactory('%s'," % mode, src)
        self.assertIn('_v65_active_router is not self', src)

    def test_builder_syntax(self):
        ast.parse(BUILDER.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
