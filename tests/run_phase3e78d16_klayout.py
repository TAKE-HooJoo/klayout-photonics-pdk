"""Phase 16: observe live accepted production candidates without changing router."""
import os,sys,csv,math
from pathlib import Path
from dataclasses import dataclass
root=os.path.abspath(os.getcwd())
if not os.path.isdir(os.path.join(root,'photonics')):
    raise RuntimeError('Run from klayout-photonics-pdk repository root')
sys.path.insert(0,root)
import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
import photonics.integration.router_hybrid_v65 as router
from tools.phase3e78d16_curvature import physical_grid_metrics,ideal_csc_jump,relative_range
from tools.live_shadow_quality_v2 import centerline_metrics

@dataclass
class Port:
    position:object
    direction:tuple
    width:float=.5

xs=WaveguideCrossSection('strip',.5,6.25)
rules=DesignRules(.4,.5,6.25)
cases=[('baseline_80_15',80,15),('offset_120_25',120,25),('negative_80_-15',80,-15)]
spacings=[.2,.1,.05,.025,.0125]
rows=[]; summaries=[]; mirror={}
for case,x,y in cases:
    lay=pya.Layout();lay.dbu=.001;cell=lay.create_cell('TOP');layer=lay.layer(pya.LayerInfo(1,0))
    src=Port(pya.DPoint(0,0),(1.,0.));dst=Port(pya.DPoint(x,y),(-1.,0.))
    captured=[]
    original=router.evaluate_route_quality
    def observer(points):
        q=original(points)
        captured.append(tuple(points))
        return q
    before=cell.shapes(layer).size()
    try:
        router.evaluate_route_quality=observer
        result=router.route_between_ports_hybrid(cell,lay,src,dst,xs,rules,mode='AUTO_QUALITY')
    finally:
        router.evaluate_route_quality=original
    delta=cell.shapes(layer).size()-before
    if delta != (1 if result.valid else 0):
        raise AssertionError('placement changed: '+case)
    refs=[]
    for mode in ('CSC','EULER'):
        ll=pya.Layout();ll.dbu=.001;cc=ll.create_cell('TOP')
        r=router.route_between_ports_hybrid(cc,ll,src,dst,xs,rules,mode=mode)
        if r.valid:refs.append(r)
    for points in captured:
        matches=[r for r in refs if len(r.points)==len(points) and all(
            abs(p.x-q.x)<1e-7 and abs(p.y-q.y)<1e-7 for p,q in zip(points,r.points))]
        if len(matches)!=1:
            raise AssertionError('candidate identification ambiguous: '+case)
        r=matches[0]
        for ds in spacings:
            m=physical_grid_metrics(points,sample_ds=ds,tangent_span=1.,derivative_span=1.)
            old_e,old_g=centerline_metrics(points,ds=ds,window=1.)
            row=dict(case=case,variant=r.variant,ds_um=ds,
                     fixed_energy_inv_um=m['energy_inv_um'],
                     fixed_gradient_inv_um2=m['gradient_inv_um2'],
                     old_energy_inv_um=old_e,old_gradient_inv_um2=old_g,
                     ideal_jump_inv_um=ideal_csc_jump(r.variant,r.designed_radius_um),
                     length_um=m['length_um'],sample_count=m['sample_count'],
                     production_variant=result.variant,shape_delta=delta,
                     scope='LIVE_CANDIDATES_FIXED_PHYSICAL_SPAN_DIAGNOSTIC')
            rows.append(row)
    print(case,'production=',result.variant,'candidates=',len(captured),'shape_delta=',delta)
for case,variant in sorted({(r['case'],r['variant']) for r in rows}):
    group=[r for r in rows if r['case']==case and r['variant']==variant]
    summaries.append(dict(case=case,variant=variant,ds_count=len(group),
        fixed_energy_relative_range=relative_range([r['fixed_energy_inv_um'] for r in group]),
        fixed_gradient_relative_range=relative_range([r['fixed_gradient_inv_um2'] for r in group]),
        old_energy_relative_range=relative_range([r['old_energy_inv_um'] for r in group]),
        old_gradient_relative_range=relative_range([r['old_gradient_inv_um2'] for r in group]),
        scope='RANGE_NOT_CONVERGENCE_PROOF'))
for ds in spacings:
    for a,b in [('EULER_SBEND','EULER_SBEND'),('LSR','RSL')]:
        pos=next((r for r in rows if r['case']=='baseline_80_15' and r['variant']==a and r['ds_um']==ds),None)
        neg=next((r for r in rows if r['case']=='negative_80_-15' and r['variant']==b and r['ds_um']==ds),None)
        if pos and neg:
            mirror[(ds,a)]=dict(ds_um=ds,positive_variant=a,negative_variant=b,
                energy_abs_diff=abs(pos['fixed_energy_inv_um']-neg['fixed_energy_inv_um']),
                gradient_abs_diff=abs(pos['fixed_gradient_inv_um2']-neg['fixed_gradient_inv_um2']))
out=Path('tests/phase3e78d16_output');out.mkdir(parents=True,exist_ok=True)
for filename,data in [('fixed_span_ds_sweep.csv',rows),('convergence_summary.csv',summaries),('mirror_symmetry.csv',list(mirror.values()))]:
    if not data:raise AssertionError('no data: '+filename)
    with (out/filename).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
print('Phase 3E-7.8D-16 diagnostic complete:',out)
