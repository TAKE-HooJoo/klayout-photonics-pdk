"""Phase 3E-7.8D-15: sampling convergence for captured live candidates.

This is a numerical centerline diagnostic, not optical loss or GDS G2 proof.
"""
import math
from tools.live_shadow_quality_v2 import centerline_metrics, shadow_scores, CSC

DS_VALUES = (0.2, 0.1, 0.05, 0.025, 0.0125)

def audit_candidates(candidates, ds_values=DS_VALUES, window=1.0, weights=(1., 1., 1., 1.)):
    """candidates: sequence of {case,variant,points,designed_radius_um}.

    Returns (per_candidate_rows, per_case_ds_summary). All metrics are recomputed
    from identical captured polylines, changing only numerical resampling ds.
    """
    if not ds_values or any(not math.isfinite(d) or d <= 0 for d in ds_values):
        raise ValueError('ds_values must be positive finite numbers')
    if not math.isfinite(window) or window <= 0:
        raise ValueError('invalid window')
    cases = {}
    for c in candidates:
        cases.setdefault(c['case'], []).append(c)
    rows, summaries = [], []
    for case, items in cases.items():
        for ds in ds_values:
            metrics = []
            for item in items:
                pts = item['points']
                length = sum(math.dist((a.x, a.y), (b.x, b.y)) for a, b in zip(pts, pts[1:]))
                energy, grad = centerline_metrics(pts, ds=ds, window=window)
                variant = item['variant']
                radius = float(item['designed_radius_um'])
                if variant in CSC:
                    if not math.isfinite(radius) or radius <= 0:
                        raise ValueError('invalid CSC radius')
                    jump = 1.0 / radius
                elif variant in ('EULER', 'EULER_SBEND'):
                    jump = 0.0
                else:
                    raise ValueError('unsupported variant '+variant)
                metrics.append(dict(case=case, variant=variant, ds_um=ds,
                                    window_um=window, length_um=length,
                                    window_energy_inv_um=energy,
                                    window_gradient_inv_um2=grad, jump_inv_um=jump))
            ranked = shadow_scores(metrics, weights=weights)
            winner = ranked[0]['variant'] if ranked else ''
            margin = ranked[1]['shadow_score'] - ranked[0]['shadow_score'] if len(ranked) > 1 else None
            summaries.append(dict(case=case, ds_um=ds, window_um=window,
                                  candidate_count=len(ranked), shadow_winner=winner,
                                  score_margin=margin, scope='SAME_CAPTURED_LIVE_CENTERLINES'))
            for r in ranked:
                rows.append(dict(r, shadow_winner=winner,
                                 scope='FIXED_WINDOW_RESAMPLED_POLYLINE_NOT_OPTICAL_LOSS'))
    return rows, summaries


def convergence_report(rows, summaries):
    """Relative range across ds, plus winner stability (not proof of convergence)."""
    grouped = {}
    for r in rows:
        grouped.setdefault((r['case'], r['variant']), []).append(r)
    result = []
    for (case, variant), items in grouped.items():
        def relrange(key):
            vals = [float(x[key]) for x in items]
            base = abs(vals[-1])
            return (max(vals) - min(vals)) / base if base > 1e-15 else (0.0 if max(vals) == min(vals) else math.inf)
        winners = {s['shadow_winner'] for s in summaries if s['case'] == case}
        result.append(dict(case=case, variant=variant, ds_count=len(items),
                           energy_relative_range=relrange('window_energy_inv_um'),
                           gradient_relative_range=relrange('window_gradient_inv_um2'),
                           score_relative_range=relrange('shadow_score'),
                           winner_stable=len(winners) == 1,
                           scope='NUMERICAL_RANGE_NOT_ANALYTIC_CONVERGENCE_PROOF'))
    return result
