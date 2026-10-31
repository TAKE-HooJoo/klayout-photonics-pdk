"""Synthetic tests for D-6; no KLayout dependency."""
import importlib.util
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('d6', ROOT/'tools/analyze_curvature_gradient.py')
d6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d6)


def run():
    assert abs(d6.declared_jump('LSR', 6.25)-0.16) < 1e-12
    assert d6.declared_jump('EULER_SBEND', 6.25) is None
    assert d6.declared_jump('LSR', 0) is None
    d5 = d6.load_d5()
    straight = [(float(x), 0.) for x in range(101)]
    for step in (0.5, 0.25, 0.1, 0.05):
        result = d6.evaluate(d5, straight, step, 1.0)
        assert abs(result['window_energy_inv_um']) < 1e-12
        assert abs(result['max_abs_window_gradient_inv_um2']) < 1e-12
    circle = [(10*math.cos(i*0.002),10*math.sin(i*0.002)) for i in range(501)]
    results = [d6.evaluate(d5, circle, step, 1.0) for step in (0.5,0.1,0.05)]
    for r in results:
        assert math.isfinite(r['max_abs_window_gradient_inv_um2'])
        assert r['window_energy_inv_um'] > 0
    print('Phase 3E-7.8D-6 synthetic tests: PASS')


if __name__ == '__main__':
    run()
