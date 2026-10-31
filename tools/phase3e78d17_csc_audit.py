"""Phase 3E-7.8D-17: CSC centerline turning-angle proxy audit.

Turning-angle proxy is not an exact analytic CSC reference. The polyline may
include discretization and endpoint artifacts. No production changes.
"""
import math

CSC = {'LSL', 'LSR', 'RSL', 'RSR'}

def turning_proxy(points, radius):
    if not math.isfinite(radius) or radius <= 0:
        raise ValueError('radius must be finite and positive')
    xy = [(float(p.x), float(p.y)) for p in points]
    if len(xy) < 3:
        raise ValueError('at least three points required')
    headings = []
    for a, b in zip(xy, xy[1:]):
        dx, dy = b[0]-a[0], b[1]-a[1]
        if math.hypot(dx,dy) < 1e-12:
            continue
        headings.append(math.atan2(dy,dx))
    if len(headings)<2:
        raise ValueError('insufficient nonzero segments')
    changes = [(b-a+math.pi)%(2*math.pi)-math.pi for a,b in zip(headings,headings[1:])]
    total_abs_angle = sum(abs(v) for v in changes)
    total_signed_angle = sum(changes)
    return {'turning_angle_abs_rad': total_abs_angle,
            'turning_angle_signed_rad': total_signed_angle,
            'arc_length_proxy_um': radius*total_abs_angle,
            'ideal_energy_proxy_inv_um': total_abs_angle/radius,
            'ideal_jump_proxy_inv_um': 1.0/radius,
            'turn_count': len(changes)}

def compare_energy(numeric_energy, ideal_proxy):
    if not math.isfinite(numeric_energy) or numeric_energy < 0:
        raise ValueError('numeric energy invalid')
    if not math.isfinite(ideal_proxy) or ideal_proxy <= 0:
        raise ValueError('ideal proxy invalid')
    return {'energy_abs_delta_inv_um': numeric_energy-ideal_proxy,
            'energy_relative_delta': (numeric_energy-ideal_proxy)/ideal_proxy}
