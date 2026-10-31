"""Live CSC audit. Run with klayout -b -r from repository root."""
import os,sys,csv,math
from pathlib import Path
root=os.path.abspath(os.getcwd())
if not os.path.isdir(os.path.join(root,'photonics')):
    raise RuntimeError('Run from klayout-photonics-pdk repository root')
sys.path.insert(0,root)
from dataclasses import dataclass
import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
import photonics.integration.router_hybrid_v65 as router
from tools.live_shadow_quality_v2 import centerline_metrics
from tools.phase3e78d17_csc_audit import turning_proxy, compare_energy

@dataclass
class Port:
    position: object
    direction: tuple
    width: float=0.5

xs=WaveguideCrossSection('strip',0.5,6.25)
rules=DesignRules(0.4,0.5,6.25)
cases=[('baseline_80_15',80,15),('offset_120_25',120,25),('negative_80_-15',80,-15)]
steps=(0.2,0.1,0.05,0.025,0.0125)
rows=[]
for name,x,y in cases:
    layout=pya.Layout();layout.dbu=0.001
    cell=layout.create_cell('TOP')
    source=Port(pya.DPoint(0,0),(1.,0.))
    destination=Port(pya.DPoint(x,y),(-1.,0.))
    result=router.route_between_ports_hybrid(cell,layout,source,destination,xs,rules,mode='CSC')
    if not result.valid or result.variant not in ('LSL','LSR','RSL','RSR'):
        raise AssertionError('CSC unavailable: '+name+' '+str(result.variant))
    proxy=turning_proxy(result.points,float(result.designed_radius_um))
    print(name,result.variant,'turn=',proxy['turning_angle_abs_rad'],'energy_proxy=',proxy['ideal_energy_proxy_inv_um'])
    for ds in steps:
        old_energy,old_grad=centerline_metrics(result.points,ds=ds,window=1.0)
        comp=compare_energy(old_energy,proxy['ideal_energy_proxy_inv_um'])
        rows.append(dict(case=name,variant=result.variant,ds_um=ds,radius_um=result.designed_radius_um,
                         old_fixed_window_energy_inv_um=old_energy,old_fixed_window_gradient_inv_um2=old_grad,
                         **proxy,**comp,
                         scope='POLYLINE_TURN_PROXY_VS_SMOOTHED_NUMERIC_NOT_EXACT_ANALYTIC'))
out=Path('tests/phase3e78d17_output');out.mkdir(parents=True,exist_ok=True)
with (out/'csc_energy_audit.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('Phase 3E-7.8D-17 diagnostic complete:',out)
