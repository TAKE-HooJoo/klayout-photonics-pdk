"""Run production AUTO_QUALITY with a temporary observer for accepted candidates."""
import os, sys
root = os.path.abspath(os.getcwd())
if not os.path.isdir(os.path.join(root,'photonics')):
    raise RuntimeError('Run from repository root')
sys.path.insert(0,root)
import csv
from pathlib import Path
from dataclasses import dataclass
import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
import photonics.integration.router_hybrid_v65 as router
from tools.live_shadow_quality_v2 import candidate_metrics, shadow_scores

@dataclass
class Port:
    position: object
    direction: tuple
    width: float = 0.5

xs=WaveguideCrossSection('strip',0.5,6.25)
rules=DesignRules(0.4,0.5,6.25)
cases=[('baseline_80_15',80,15),('offset_120_25',120,25),('negative_80_-15',80,-15)]
rows=[]; summaries=[]
for case,x,y in cases:
    layout=pya.Layout();layout.dbu=0.001
    cell=layout.create_cell('TOP')
    layer=layout.layer(pya.LayerInfo(1,0))
    source=Port(pya.DPoint(0,0),(1.,0.))
    destination=Port(pya.DPoint(x,y),(-1.,0.))
    captured=[]
    original=router.evaluate_route_quality
    def observe(points):
        # Call production's evaluator first; preserve its exceptions and result.
        q=original(points)
        captured.append((tuple(points),q))
        return q
    before=cell.shapes(layer).size()
    try:
        router.evaluate_route_quality=observe
        result=router.route_between_ports_hybrid(cell,layout,source,destination,xs,rules,mode='AUTO_QUALITY')
    finally:
        router.evaluate_route_quality=original
    delta=cell.shapes(layer).size()-before
    if result.valid and delta!=1 or not result.valid and delta!=0:
        raise AssertionError('unexpected placement delta for '+case)
    # Each accepted candidate invokes evaluate_route_quality once; variant
    # must be identified independently from point count, not guessed by score.
    # CSC is distinguished via designed-radius metadata unavailable in callback;
    # reconstruct by matching production CSC/EULER runs against point sequences.
    reference=[]
    for mode in ('CSC','EULER'):
        lay=pya.Layout();lay.dbu=0.001; c=lay.create_cell('TOP')
        r=router.route_between_ports_hybrid(c,lay,source,destination,xs,rules,mode=mode)
        if r.valid:
            reference.append(r)
    def matches(points, ref):
        return len(points)==len(ref.points) and all(
            abs(p.x-q.x)<1e-7 and abs(p.y-q.y)<1e-7 for p,q in zip(points,ref.points))
    metrics=[]
    for points,q in captured:
        match=[r for r in reference if matches(points,r)]
        if len(match)!=1:
            raise AssertionError('candidate not uniquely matched to CSC/EULER: '+case)
        ref=match[0]
        radius=ref.designed_radius_um
        metric=candidate_metrics(points,ref.variant,radius)
        metrics.append(dict(case=case,variant=ref.variant,production_energy_inv_um=q.curvature_energy_inv_um,
                            designed_radius_um=radius,**metric))
    scored=shadow_scores(metrics)
    winner=scored[0]['variant'] if scored else ''
    for item in scored:
        rows.append(dict(item,production_variant=result.variant,shadow_winner=winner,
                         production_valid=result.valid,shape_delta=delta,
                         scope='LIVE_ACCEPTED_CANDIDATES_IDEAL_JUMP_PROXY'))
    summaries.append(dict(case=case,production_variant=result.variant,shadow_winner=winner,
                          candidate_count=len(scored),match=str(result.variant==winner) if scored else 'NO_CANDIDATES',
                          shape_delta=delta,scope='LIVE_SAME_ACCEPTED_CANDIDATES'))
    print(case,'production=',result.variant,'shadow=',winner,'candidates=',len(scored),'delta=',delta)

out=Path('tests/phase3e78d14_output');out.mkdir(parents=True,exist_ok=True)
for name,data in [('live_candidate_scores.csv',rows),('live_comparison.csv',summaries)]:
    with (out/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
print('Phase 3E-7.8D-14 live candidate audit complete:',out)
