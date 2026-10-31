"""Run with python3 tests/test_curvature_window.py (no pytest needed)."""
import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'tools'))
from analyze_curvature_window import evaluate

straight=[(i*0.1,0.) for i in range(1001)]
for ds in (0.5,0.25,0.1,0.05):
    result=evaluate(straight,ds,1.)
    assert result['window_energy_inv_um'] < 1e-20, result
    assert result['max_abs_kappa_inv_um'] < 1e-10, result

radius=10.
circle=[(radius*math.cos(i*math.pi/2000),radius*math.sin(i*math.pi/2000)) for i in range(2001)]
energies=[]
for ds in (0.5,0.25,0.1,0.05):
    result=evaluate(circle,ds,1.)
    assert abs(result['max_abs_kappa_inv_um']-0.1) < 0.002, result
    energies.append(result['window_energy_inv_um'])
assert (max(energies)-min(energies))/max(energies) < 0.002, energies
print('Phase 3E-7.8D-5 synthetic tests: PASS')
