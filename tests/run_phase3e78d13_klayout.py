import os
import sys

# KLayout -b -r macro environment bootstrap
PROJECT_ROOT = os.path.abspath(os.getcwd())

if not os.path.isdir(os.path.join(PROJECT_ROOT, "photonics")):
    raise RuntimeError(
        "Run this macro from the klayout-photonics-pdk repository root"
    )

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

"""KLayout batch production AUTO_QUALITY regression; does not modify router."""
import csv
from dataclasses import dataclass
from pathlib import Path
import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.router_hybrid_v65 import route_between_ports_hybrid

@dataclass
class Port:
    position: object
    direction: tuple
    width: float = 0.5

xs=WaveguideCrossSection('strip',0.5,6.25)
rules=DesignRules(0.4,0.5,6.25)
cases=[('baseline_80_15',80,15),('offset_120_25',120,25),('negative_80_-15',80,-15)]
rows=[]
for case,x,y in cases:
    for mode in ('AUTO_QUALITY','CSC','EULER'):
        layout=pya.Layout();layout.dbu=0.001
        cell=layout.create_cell('TOP')
        layer=layout.layer(pya.LayerInfo(1,0))
        source=Port(pya.DPoint(0,0),(1.,0.))
        destination=Port(pya.DPoint(x,y),(-1.,0.))
        before=cell.shapes(layer).size()
        r=route_between_ports_hybrid(cell,layout,source,destination,xs,rules,mode=mode)
        after=cell.shapes(layer).size()
        delta=after-before
        if r.valid and delta!=1:
            raise AssertionError('valid route must insert exactly one shape: '+case+'/'+mode)
        if not r.valid and delta!=0:
            raise AssertionError('invalid route must not insert a shape: '+case+'/'+mode)
        row=dict(case=case,mode=mode,valid=str(bool(r.valid)),variant=r.variant,
                 reason=r.reason or '',length_um='%.12g'%r.length_um,
                 designed_radius_um='%.12g'%getattr(r,'designed_radius_um',float('nan')),
                 sampled_radius_um='%.12g'%getattr(r,'sampled_min_radius_um',getattr(r,'sampled_radius_um',float('nan'))),
                 point_count=len(r.points),shape_delta=delta)
        rows.append(row)
        print('%-17s %-13s valid=%s variant=%s length=%s delta=%s'%(case,mode,row['valid'],r.variant,row['length_um'],delta))
out=Path('tests/phase3e78d13_output/production_routes.csv')
out.parent.mkdir(parents=True,exist_ok=True)
with out.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('Production routing complete:',out)
