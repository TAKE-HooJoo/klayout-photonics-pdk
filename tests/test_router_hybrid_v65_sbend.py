"""Phase 3E-7.7C: Hybrid Router Euler S-Bend selection test.

Run:
    klayout -b -r tests/test_router_hybrid_v65_sbend.py
"""
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.getcwd())

import pya

from photonics.pdk.cross_section import WaveguideCrossSection
from photonics.pdk.design_rules import DesignRules
from photonics.integration.router_hybrid_v65 import route_between_ports_hybrid


@dataclass
class Port:
    position: object
    direction: tuple
    width: float = 0.5


xs = WaveguideCrossSection('strip', 0.5, 6.25)
rules = DesignRules(0.4, 0.5, 6.25)

source = Port(pya.DPoint(0, 0), (1.0, 0.0))
destination = Port(pya.DPoint(80, 15), (-1.0, 0.0))

outdir = os.path.join(
    os.getcwd(), 'tests', 'phase3e77c_output'
)
os.makedirs(outdir, exist_ok=True)


def make_layout(keepout=None):
    ly = pya.Layout()
    ly.dbu = 0.001
    cell = ly.create_cell('HYBRID_SBEND_TEST')

    if keepout is not None:
        layer = ly.layer(pya.LayerInfo(90, 0))
        cell.shapes(layer).insert(
            pya.DBox(*keepout).to_itype(ly.dbu)
        )

    return ly, cell


def run_case(name, mode, expected_variant=None, keepout=None,
             expect_valid=True):
    ly, cell = make_layout(keepout)

    wg = ly.layer(pya.LayerInfo(1, 0))
    before = cell.shapes(wg).size()

    result = route_between_ports_hybrid(
        cell, ly, source, destination,
        xs, rules, mode=mode
    )

    after = cell.shapes(wg).size()

    print(
        '%s: valid=%s variant=%s reason=%s '
        'length=%.6f radius=%.6f shapes=%d->%d'
        % (
            name, result.valid, result.variant,
            result.reason, result.length_um,
            result.measured_radius_um,
            before, after
        )
    )

    assert result.valid == expect_valid, (
        name, result.reason
    )

    if expect_valid:
        assert after > before, (
            name, 'No waveguide inserted'
        )

        if expected_variant is not None:
            assert result.variant == expected_variant, (
                name, result.variant
            )

        assert result.tangent_error_source_deg <= 5.0
        assert result.tangent_error_destination_deg <= 5.0

    else:
        assert after == before, (
            name, 'GDS mutated on failure'
        )

    path = os.path.join(outdir, name + '.gds')
    ly.write(path)

    return result


# Case 1: AUTO should prefer Euler S-Bend.
run_case(
    'hybrid_auto_sbend',
    'AUTO',
    expected_variant='EULER_SBEND'
)

# Case 2: EULER mode should also support S-Bend.
run_case(
    'hybrid_euler_sbend',
    'EULER',
    expected_variant='EULER_SBEND'
)

# Case 3: CSC-only mode must remain functional.
run_case(
    'hybrid_csc_parallel',
    'CSC'
)

# Case 4: Keepout encloses source.
# No route is allowed to leave the source.
run_case(
    'hybrid_auto_blocked',
    'AUTO',
    keepout=(-3, -3, 3, 3),
    expect_valid=False
)

print('Phase 3E-7.7C Hybrid Euler S-Bend: PASS')
