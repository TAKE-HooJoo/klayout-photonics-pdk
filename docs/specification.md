# Functional Specification

**Document version:** 0.1  
**Target:** KLayout 0.30.9  
**Status:** provisional

## 1. Purpose

This repository contains an experimental silicon-photonics PCell library and an interactive waveguide-routing plugin for KLayout. The current implementation is intended for geometry development, education, and routing experiments.

It is **not yet a foundry-qualified photonics PDK**.

## 2. System configuration

| Item | Specification |
|---|---|
| KLayout | 0.30.9 |
| PCell library | Simple Silicon Photonics PCell Library v4 |
| Library registration name | `Photonics` |
| Router | Photonics Router v5.x |
| Waveguide layer | `1/0` |
| Optical pin layer | `2/0` |
| Default waveguide width | `0.5 µm` |
| Macro directory | `~/.klayout/pymacros/` |

## 3. PCells

| PCell | Function |
|---|---|
| Straight | Parameterized straight waveguide |
| Bend90 | 90-degree bend |
| EulerBend | Approximate smooth-curvature bend |
| SBend | Smooth lateral/vertical offset |
| Ring | Ring-resonator geometry with bus waveguide |
| DirectionalCoupler | Coupling section with smooth access S-bends |
| MMI_1x2 | 1x2 MMI geometry |
| MZI | Mach-Zehnder interferometer geometry |
| WaveguideRoute | Cubic-Bézier waveguide between relative endpoints |
| PortConnector | Short straight connector with optical ports |

## 4. Optical ports

Optical port information is generated on layer `2/0`.

- Port names use `opt1`, `opt2`, etc.
- Text is placed at the optical interface.
- A short pin path represents the port position and direction.
- The router is designed to transform hierarchical pin geometry into top-cell coordinates before routing.

## 5. Router development status

| Version | Feature | Status |
|---|---|---|
| v5.1 | Two-click interactive waveguide creation | Tested |
| v5.2 | Optical-port position snapping | Tested |
| v5.3 | Port-direction recognition | Failed due to incompatible `Path.point` API usage |
| v5.3.1 | First `each_point` correction | Failed; old API reference remained |
| v5.3.2 | Rebuilt direction-aware router using `Shape.each_point()` | Verification pending |

## 6. Router v5.3.2 behavior

1. Select `Photonics Router v5.3.2`.
2. Click near the first optical pin.
3. Search pin paths on `2/0` within the snap radius.
4. Snap to the selected pin endpoint and derive its direction vector.
5. Click near the second optical pin.
6. Snap and derive the second port direction.
7. Generate a cubic Bézier centerline whose endpoint tangents follow the port directions.
8. Insert a `0.5 µm` wide path on `1/0`.

### Current parameters

| Parameter | Value |
|---|---:|
| `WG_WIDTH` | `0.5 µm` |
| `SNAP_RADIUS` | `4.0 µm` |
| `LEAD` | `8.0 µm` |
| `NPTS` | `80` |
| `WG_LAYER` | `1/0` |
| `PIN_LAYER` | `2/0` |

## 7. Installation

Keep only the current router version together with the PCell library:

```text
~/.klayout/pymacros/
├── photonics_pdk_v4.lym
└── photonics_router_v5_3_2.lym
```

Fully restart KLayout after replacing a macro.

## 8. Known limitations

- Component dimensions are generic geometry defaults, not process-qualified values.
- `EulerBend` is an approximation rather than a mathematically exact clothoid implementation.
- `WaveguideRoute` and the current router use cubic Bézier geometry.
- Minimum bend radius is not yet rigorously guaranteed.
- Obstacle avoidance and DRC-aware routing are not implemented.
- Port-width inheritance and automatic taper insertion are not implemented.
- Optical path-length matching and meander generation are not implemented.
- TE/TM mode metadata and photonic net attributes are not implemented.
- Router v5.3.2 still requires final verification in KLayout 0.30.9.

## 9. Planned development

### v5.4
- stabilize direction-aware routing
- visual feedback for selected/snapped ports
- clearer routing-state indication

### v5.5
- minimum-radius-aware Euler/arc routing

### v6
- obstacle avoidance
- DRC-aware routing
- width/layer inheritance from ports

### Future
- optical path-length matching
- MZI differential-length control
- meander routing
- circuit/netlist connectivity integration

## 10. v5.3.2 verification checklist

- [ ] Plugin starts without a script error.
- [ ] Both clicks snap to the intended `2/0` optical ports.
- [ ] Start tangent follows the first pin direction.
- [ ] End tangent follows the second pin direction.
- [ ] Generated waveguide is on `1/0`.
- [ ] Generated waveguide width is `0.5 µm`.
- [ ] Hierarchical PCell ports are transformed correctly into top-cell coordinates.
