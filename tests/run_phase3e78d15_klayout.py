"""Capture AUTO_QUALITY accepted centerlines, then sweep ds without mutation."""
import os
import sys
root = os.path.abspath(os.getcwd())
if not os.path.isdir(os.path.join(root, 'photonics')):
    raise RuntimeError('Run from klayout-photonics-pdk repository root')
if root not in sys.path:
    sys.path.insert(0, root)
import csv
from pathlib import Path
from dataclasses import dataclass
import pya
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
import photonics.integration.router_hybrid_v65 as router
from tools.audit_live_shadow_convergence import audit_candidates, convergence_report, DS_VALUES

@dataclass
class Port:
    position: object
    direction: tuple
    width: float = 0.5

xs = WaveguideCrossSection('strip', 0.5, 6.25)
rules = DesignRules(0.4, 0.5, 6.25)
cases = [('baseline_80_15', 80, 15), ('offset_120_25', 120, 25),
         ('negative_80_-15', 80, -15)]
all_candidates = []
production_rows = []
for case, x, y in cases:
    layout = pya.Layout()
    layout.dbu = 0.001
    cell = layout.create_cell('TOP')
    layer = layout.layer(pya.LayerInfo(1, 0))
    source = Port(pya.DPoint(0, 0), (1., 0.))
    destination = Port(pya.DPoint(x, y), (-1., 0.))
    captured = []
    original = router.evaluate_route_quality
    def observe(points):
        quality = original(points)
        captured.append(tuple(points))
        return quality
    before = cell.shapes(layer).size()
    try:
        router.evaluate_route_quality = observe
        result = router.route_between_ports_hybrid(cell, layout, source, destination,
                                                   xs, rules, mode='AUTO_QUALITY')
    finally:
        router.evaluate_route_quality = original
    delta = cell.shapes(layer).size() - before
    if delta != (1 if result.valid else 0):
        raise AssertionError('unexpected shape delta: ' + case)
    refs = []
    for mode in ('CSC', 'EULER'):
        lay = pya.Layout()
        lay.dbu = 0.001
        refcell = lay.create_cell('TOP')
        ref = router.route_between_ports_hybrid(refcell, lay, source, destination,
                                                xs, rules, mode=mode)
        if ref.valid:
            refs.append(ref)
    def matches(pts, ref):
        return len(pts) == len(ref.points) and all(
            abs(p.x-q.x) < 1e-7 and abs(p.y-q.y) < 1e-7
            for p, q in zip(pts, ref.points))
    for pts in captured:
        matching = [r for r in refs if matches(pts, r)]
        if len(matching) != 1:
            raise AssertionError('candidate not uniquely matched: '+case)
        ref = matching[0]
        all_candidates.append(dict(case=case, variant=ref.variant, points=pts,
                                   designed_radius_um=ref.designed_radius_um))
    production_rows.append(dict(case=case, production_variant=result.variant,
                                production_valid=result.valid, candidate_count=len(captured),
                                shape_delta=delta, scope='LIVE_AUTO_QUALITY_ACCEPTED'))

rows, summaries = audit_candidates(all_candidates)
report = convergence_report(rows, summaries)
prod = {r['case']:r for r in production_rows}
for s in summaries:
    s['production_variant'] = prod[s['case']]['production_variant']
    s['production_match'] = s['shadow_winner'] == s['production_variant']
    s['shape_delta'] = prod[s['case']]['shape_delta']
for r in rows:
    r['production_variant'] = prod[r['case']]['production_variant']
    r['shape_delta'] = prod[r['case']]['shape_delta']

# Explicit mirror-symmetry checks at every ds for the two mirror cases.
symmetry = []
for ds in DS_VALUES:
    for variant_a, variant_b in [('EULER_SBEND', 'EULER_SBEND'), ('LSR', 'RSL')]:
        a = next((r for r in rows if r['case']=='baseline_80_15' and r['variant']==variant_a and r['ds_um']==ds), None)
        b = next((r for r in rows if r['case']=='negative_80_-15' and r['variant']==variant_b and r['ds_um']==ds), None)
        if a is None or b is None:
            raise AssertionError('missing mirror candidates')
        e_diff = abs(a['window_energy_inv_um']-b['window_energy_inv_um'])
        g_diff = abs(a['window_gradient_inv_um2']-b['window_gradient_inv_um2'])
        s_diff = abs(a['shadow_score']-b['shadow_score'])
        symmetry.append(dict(ds_um=ds, positive_variant=variant_a, negative_variant=variant_b,
                             energy_abs_diff=e_diff, gradient_abs_diff=g_diff,
                             score_abs_diff=s_diff, pass_tolerance=(max(e_diff,g_diff,s_diff)<1e-6)))

out = Path('tests/phase3e78d15_output')
out.mkdir(parents=True, exist_ok=True)
def save(name, data):
    if not data:
        raise AssertionError('empty output '+name)
    with (out/name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]))
        w.writeheader()
        w.writerows(data)
save('ds_sweep_candidate_scores.csv', rows)
save('ds_sweep_winners.csv', summaries)
save('convergence_summary.csv', report)
save('mirror_symmetry.csv', symmetry)
save('production_reference.csv', production_rows)
for s in summaries:
    print('%-16s ds=%-7g production=%-12s shadow=%-12s candidates=%d' %
          (s['case'], s['ds_um'], s['production_variant'], s['shadow_winner'], s['candidate_count']))
print('Phase 3E-7.8D-15: numeric ds sweep complete (not optical loss or GDS proof):', out)
