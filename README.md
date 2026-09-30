# KLayout Silicon Photonics PDK

Experimental silicon-photonics PCell library and interactive waveguide router for **KLayout 0.30.9**.

> Status: early development / geometry prototype. This is not a foundry-qualified photonics PDK.

## Current contents

### PCell library v4

Registered KLayout library: `Photonics`

- Straight
- Bend90
- EulerBend
- SBend
- Ring
- DirectionalCoupler
- MMI_1x2
- MZI
- WaveguideRoute
- PortConnector

### Photonics Router

- **v5.1**: two-click interactive routing — tested
- **v5.2**: automatic optical-port position snapping — tested
- **v5.3.2**: port-position + port-direction routing — implementation ready, KLayout 0.30.9 verification pending

## Layers

| Purpose | Layer/Datatype |
|---|---:|
| Waveguide | `1/0` |
| Optical pins | `2/0` |

The PCells use optical port names such as `opt1`, `opt2`, etc.

## Installation

Copy the current PCell library and router macro into:

```text
~/.klayout/pymacros/
```

Recommended current setup:

```text
~/.klayout/pymacros/
├── photonics_pdk_v4.lym
└── photonics_router_v5_3_2.lym
```

Remove or move older router versions out of `pymacros` to avoid duplicate plugin registration, then fully restart KLayout.

## Router usage

1. Open a layout containing the photonics PCells.
2. Select `Photonics Router v5.3.2` from the toolbar.
3. Click near the first optical port.
4. Click near the second optical port.
5. The router creates a waveguide on `1/0`.

Current defaults:

- waveguide width: `0.5 µm`
- optical pin layer: `2/0`
- snap radius: `4.0 µm`
- Bézier sampling points: `80`

See [docs/specification.md](docs/specification.md) for details and known limitations.

## Repository layout

```text
.
├── README.md
├── LICENSE
├── .gitignore
├── pymacros/
│   ├── photonics_pdk_v4.lym
│   └── photonics_router_v5_3_2.lym
├── docs/
│   ├── specification.md
│   └── KLayout_Silicon_Photonics_PCell_Router_Spec_v0.1.docx
├── examples/
└── tests/
```

## Important limitations

The current cells and router are intended for layout prototyping and development. Component dimensions are not yet tied to a validated fabrication process or optical simulation model. The router is Bézier-based and does not yet mathematically guarantee minimum bend radius, DRC-aware obstacle avoidance, path-length matching, or automatic taper insertion.

## Versioning plan

- `v0.1.0`: PCell v4 + experimental Router v5.3.x
- `v0.2.0`: stable port-aware router
- `v0.3.0`: bend-radius-aware routing
- `v1.0.0`: first stable release

## License

MIT License. See [LICENSE](LICENSE).
