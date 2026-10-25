"""KLayout smoke test: reject noncompliant smoothing rather than output a bad GDS."""
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import pya
from photonics.circuit.geometry import Point
from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.obstacle_router_v2 import route_with_waypoints
from photonics.integration.obstacle_router_v3 import route_with_smooth_waypoints
from photonics.routing.continuity import sharp_corners, turn_angles_deg
from photonics.routing.geometry import min_radius


def main():
    layout = pya.Layout()
    layout.dbu = 0.001
    xs = WaveguideCrossSection('strip', 0.5, 5.0)
    rules = DesignRules(0.4, 0.5, 5.0)
    blocker = pya.Region(
        pya.DBox(37, -3, 43, 3).to_itype(layout.dbu)
    )

    args = (
        Point(0, 0),
        Point(80, 0),
        (1, 0),
        (-1, 0),
        xs,
        rules,
        layout,
        blocker,
    )
    baseline = route_with_waypoints(*args)
    assert baseline.valid, baseline

    print('Baseline length: %.3f um' % baseline.length_um)
    print('Baseline sharp corners:', sharp_corners(baseline.points))

# === Phase 3E-5.2: 曲率診断を追加 ===
    angles = turn_angles_deg(baseline.points)

    print('Point count:', len(baseline.points))
    print('Maximum turn: %.6f deg' % max(angles))
    print('Minimum 3-point radius: %.6f um' %
          min_radius(baseline.points))
    print('Designed radius: %.6f um' %
          baseline.designed_radius_um)
    print('Measured radius: %.6f um' %
          baseline.measured_radius_um)

# === 既存の平滑化テスト ===
    smooth = route_with_smooth_waypoints(*args)
    if smooth.valid:
        assert not sharp_corners(smooth.points, 5.0)
        print('G1-smoothed route: PASS; length %.3f um' % smooth.length_um)
    else:
        assert smooth.reason in ('FILLET_GEOMETRY_INFEASIBLE',
                                 'FILLET_CLEARANCE_VIOLATION',
                                 'FILLET_PORT_TANGENT_ERROR',
                                 'FILLET_REMAINING_KINK'), smooth
        print('Unsafe fillet correctly rejected:', smooth.reason)
    print('Phase 3E-5.1 diagnostic integration: PASS')

if __name__ == '__main__':
    main()
