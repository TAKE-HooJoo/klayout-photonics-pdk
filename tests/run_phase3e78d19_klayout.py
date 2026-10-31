"""KLayout: audit direct CSC parameters, without changing Production routing."""
import os,sys,csv,math
from pathlib import Path
from dataclasses import dataclass
root=os.path.abspath(os.getcwd())
if not os.path.isdir(os.path.join(root,'photonics')):
    raise RuntimeError('Run from repository root')
sys.path.insert(0,root)
import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.circuit.geometry import Point
from photonics.integration.router_hybrid_v65 import route_between_ports_hybrid
from tools.phase3e78d19_csc_match import reconstruct_matches
@dataclass
class Port:
    position:object
    direction:tuple
    width:float=.5
xs=WaveguideCrossSection('strip',.5,6.25)
rules=DesignRules(.4,.5,6.25)
out=Path('tests/phase3e78d19_output');out.mkdir(parents=True,exist_ok=True)
rows=[]
for case,x,y in [('baseline_80_15',80,15),('offset_120_25',120,25),('negative_80_-15',80,-15)]:
    layout=pya.Layout();layout.dbu=.001;cell=layout.create_cell('TOP')
    src=Port(pya.DPoint(0,0),(1.,0.));dst=Port(pya.DPoint(x,y),(-1.,0.))
    result=route_between_ports_hybrid(cell,layout,src,dst,xs,rules,mode='CSC')
    if not result.valid:
        raise AssertionError('CSC invalid: '+case+' '+str(result.reason))
    radius=float(result.designed_radius_um)
    matches=reconstruct_matches(result,Point(0,0),Point(x,y),src.direction,dst.direction,radius)
    shape_delta=cell.shapes(layout.layer(pya.LayerInfo(1,0))).size()
    if shape_delta!=1:
        raise AssertionError('Unexpected shape count: '+case)
    status='EXACT_MATCHED' if len(matches)==1 else ('AMBIGUOUS_MATCH' if matches else 'NOT_MATCHED')
    m=matches[0] if len(matches)==1 else {}
    row={'case':case,'variant':result.variant,'status':status,'matches':len(matches),
         'radius_um':radius,'polyline_length_um':result.length_um,
         'arc1_rad':m.get('arc1_rad',''),'arc2_rad':m.get('arc2_rad',''),
         'straight_um':m.get('straight_um',''),
         'analytic_length_um':m.get('analytic_length_um',''),
         'analytic_energy_inv_um':m.get('analytic_energy_inv_um',''),
         'ideal_jump_inv_um':m.get('ideal_jump_inv_um',''),
         'point_max_error_um':m.get('point_max_error_um',''),
         'shape_delta':shape_delta}
    rows.append(row)
    print(case,result.variant,status,'energy=',m.get('analytic_energy_inv_um','NOT_AVAILABLE'))
with (out/'csc_exact_parameter_audit.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
if any(r['status']!='EXACT_MATCHED' for r in rows):
    print('WARNING: some cases did not match; see CSV. No analytic values were guessed.')
print('Phase 19 audit complete:',out)
