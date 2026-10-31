import importlib.util
import math
from pathlib import Path

p=Path(__file__).resolve().parent.parent/'tools/analyze_curvature_integrated.py'
s=importlib.util.spec_from_file_location('d7',p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
base={'designed_radius_um':'7.8125','ideal_csc_line_arc_jump_inv_um':'0.128'}
assert m.validate_jump(base)[0]=='CONSISTENT'
assert m.validate_jump({**base,'designed_radius_um':'6.25'})[0]=='MISMATCH'
assert m.validate_jump({**base,'ideal_csc_line_arc_jump_inv_um':''})[0]=='NOT_AVAILABLE'
assert m.experimental_score(1,1,1,None,[1]*4,[1]*4) is None
assert math.isclose(m.experimental_score(1,2,3,0,[1,2,3,1],[1]*4),3)
assert math.isclose(m.convergence([
 {'actual_step_um':'0.1','max_abs_window_gradient_inv_um2':'0.02'},
 {'actual_step_um':'0.05','max_abs_window_gradient_inv_um2':'0.025'}])['relative_change'],0.2)
print('Phase 3E-7.8D-7 synthetic tests: PASS')
