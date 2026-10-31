"""Source/provenance audit. No production router changes or guessed analytic angles."""
import os,sys,csv,inspect
from pathlib import Path
root=os.path.abspath(os.getcwd())
if not os.path.isdir(os.path.join(root,'photonics')): raise RuntimeError('Run from repository root')
sys.path.insert(0,root)
from dataclasses import dataclass
import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
import photonics.integration.router_hybrid_v65 as router
from tools.phase3e78d18_csc import audit_source,parameter_status,analytic_csc_energy
from tools.phase3e78d17_csc_audit import turning_proxy
@dataclass
class Port:
 position:object
 direction:tuple
 width:float=.5
xs=WaveguideCrossSection('strip',.5,6.25)
rules=DesignRules(.4,.5,6.25)
out=Path('tests/phase3e78d18_output');out.mkdir(parents=True,exist_ok=True)
rows=[]
for case,x,y in [('baseline_80_15',80,15),('offset_120_25',120,25),('negative_80_-15',80,-15)]:
 layout=pya.Layout();layout.dbu=.001;cell=layout.create_cell('TOP')
 src=Port(pya.DPoint(0,0),(1.,0.));dst=Port(pya.DPoint(x,y),(-1.,0.))
 r=router.route_between_ports_hybrid(cell,layout,src,dst,xs,rules,mode='CSC')
 if not r.valid: raise AssertionError('CSC invalid: '+case)
 p=turning_proxy(r.points,float(r.designed_radius_um))
 params=parameter_status(r)
 exact=analytic_csc_energy(float(r.designed_radius_um),**params) if params is not None else None
 rows.append(dict(case=case,variant=r.variant,designed_radius_um=r.designed_radius_um,
     polyline_turn_proxy_rad=p['turning_angle_abs_rad'],polyline_energy_proxy_inv_um=p['ideal_energy_proxy_inv_um'],
     analytic_energy_inv_um=exact['analytic_energy_inv_um'] if exact else '',
     arc1_rad=params['arc1_rad'] if params else '',arc2_rad=params['arc2_rad'] if params else '',
     straight_um=params['straight_um'] if params else '',
     provenance='EXACT_EXPOSED_PARAMETERS' if exact else 'EXACT_PARAMETERS_NOT_EXPOSED',
     shape_delta=cell.shapes(layout.layer(pya.LayerInfo(1,0))).size()))
 print(case,r.variant,'proxy=',p['ideal_energy_proxy_inv_um'],'exact=',exact['analytic_energy_inv_um'] if exact else 'NOT_EXPOSED')
with (out/'csc_parameter_provenance.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with (out/'source_locations.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['symbol','status','source_location']);w.writerows(audit_source(router))
print('Phase 18 provenance audit complete:',out)
