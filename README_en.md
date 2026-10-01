# KLayout Silicon Photonics PDK

[日本語](README.md)

An open-source Silicon Photonics PCell library and interactive waveguide router for **KLayout 0.30.9**.

> **Development status:** Early development / geometry prototype  
> This project is currently **not a foundry-qualified Silicon Photonics PDK**.

---

## Overview

This project uses KLayout PCells (Parameterized Cells) to parametrically generate basic optical devices for Silicon Photonics.

It also includes the development of an interactive **Photonics Router** for connecting optical ports between PCells with waveguides.

The main goals of this project are:

- Learning and experimenting with Silicon Photonics layout using KLayout
- Parametric generation of optical devices using PCells
- Waveguide routing using optical ports
- Development of an open-source Silicon Photonics PDK
- Education in Silicon Photonics layout design
- Exploration of Photonics CAD functionality using the KLayout Python API

---

## Supported Environment

The project is currently developed and evaluated with:

- KLayout `0.30.9`
- KLayout Python API
- Linux

The KLayout Python API may differ between KLayout versions, so some functions may not work correctly with other versions.

---

# PCell Library

## PCell Library v4

Registered KLayout library name:

`Photonics`

The library currently contains the following 10 PCells:

| PCell | Function |
|---|---|
| `Straight` | Straight waveguide |
| `Bend90` | 90-degree bend |
| `EulerBend` | Euler-type bend |
| `SBend` | S-bend |
| `Ring` | Ring resonator |
| `DirectionalCoupler` | Directional coupler |
| `MMI_1x2` | 1x2 MMI |
| `MZI` | Mach-Zehnder Interferometer |
| `WaveguideRoute` | Bézier-curve waveguide |
| `PortConnector` | Optical port connection waveguide |

---

## Straight

Generates a straight waveguide.

Main parameters:

- Length
- Width

Optical ports are generated at both ends of the waveguide.

---

## Bend90

Generates a 90-degree waveguide bend.

It can be used to change the propagation direction of a waveguide by 90 degrees.

---

## EulerBend

Generates an Euler-type bend with a smoothly varying curvature profile.

The current implementation is an approximate geometry intended for layout experiments. It does not guarantee an exact Clothoid / Euler curve.

---

## SBend

Generates an S-shaped waveguide for smoothly connecting two waveguides at different positions.

It can be used for optical port alignment between devices.

---

## Ring

Generates the basic geometry of a ring resonator.

The structure consists of a ring waveguide and a bus waveguide.

---

## DirectionalCoupler

Generates a directional coupler consisting of two closely spaced waveguides.

Smooth S-bends are used for the access sections.

---

## MMI_1x2

Generates a 1-input / 2-output MMI (Multi-Mode Interferometer).

Basic structure:

- 1 input port
- MMI body
- 2 output ports

---

## MZI

Generates a Mach-Zehnder Interferometer.

Basic structure:

- Input MMI
- Two optical waveguide arms
- Output MMI
- S-bends for separation and recombination

The current implementation is intended primarily for basic geometry generation.

---

## WaveguideRoute

Generates a smooth waveguide from the relative position of the start and end points.

Main parameters:

- `dx`
- `dy`
- `width`
- `radius`

The current implementation uses a cubic Bézier curve.

The `radius` parameter is used to influence the curve geometry and does not guarantee a strict minimum bend radius.

---

## PortConnector

Generates a short straight waveguide for optical port connections.

Optical ports are generated at both ends:

- `opt1`
- `opt2`

---

# Optical Ports

Optical port information is generated on Layer `2/0`.

Typical port names are:

```text
opt1
opt2
opt3
...
```

Optical ports are intended to represent:

- Port position
- Port name
- Connection direction

A short Pin Path is placed at each optical interface so that the Photonics Router can identify the port position and direction.

---

# Layer Definition

The current basic layer definitions are:

| Purpose | Layer / Datatype |
|---|---:|
| Waveguide | `1/0` |
| Optical Pin | `2/0` |

### Layer 1/0

Used for Silicon Photonics waveguide geometry.

### Layer 2/0

Used for optical port information.

This layer mainly contains:

- Pin Paths
- `opt1`
- `opt2`
- Other optical port information

---

# Photonics Router

An interactive router is being developed to connect PCells with optical waveguides.

The basic interaction concept is:

```text
Click start port
       ↓
Click destination port
       ↓
Generate waveguide automatically
```

---

## Router Development History

| Version | Function | Status |
|---|---|---|
| v5.1 | Two-click waveguide generation | Verified |
| v5.2 | Automatic snapping to optical ports | Verified |
| v5.3 | Port-direction detection | API compatibility issue |
| v5.3.1 | `each_point()` support | Under revision |
| v5.3.2 | Rebuilt position + direction-aware router | Under evaluation |

---

## Router v5.1

The first interactive router implementation.

Clicking two points generates a waveguide connecting them.

```text
Click 1
   ↓
Click 2
   ↓
Waveguide
```

---

## Router v5.2

Adds automatic snapping to optical ports.

When an optical port on Layer `2/0` is located near the clicked position, the router automatically snaps to the port position.

This makes it easier to accurately connect a generated waveguide to a PCell optical port.

---

## Router v5.3.x

This version is being developed to recognize not only the optical port position but also the **port direction**.

The goal is to align the tangent direction of the generated waveguide with the direction of the optical port.

The direction vector is obtained from the Pin Path on Layer `2/0` and used to determine the waveguide endpoint tangent.

---

## Router v5.3.2

This version rebuilds the port-direction detection mechanism for compatibility with the KLayout 0.30.9 Python API.

Basic processing flow:

1. Click near the first optical port
2. Search for a Pin Path on Layer `2/0`
3. Snap to the optical port position
4. Determine the port direction from the Pin Path
5. Click near the second optical port
6. Determine its position and direction
7. Generate a curve using both port directions
8. Create the waveguide on Layer `1/0`

The implementation is currently being evaluated with KLayout 0.30.9.

---

# Router Parameters

The current v5.3.2 implementation uses the following parameters:

| Parameter | Value | Description |
|---|---:|---|
| `WG_WIDTH` | `0.5 µm` | Waveguide width |
| `SNAP_RADIUS` | `4.0 µm` | Optical port search radius |
| `LEAD` | `8.0 µm` | Control distance for port direction |
| `NPTS` | `80` | Number of Bézier curve points |
| `WG_LAYER` | `1/0` | Waveguide layer |
| `PIN_LAYER` | `2/0` | Optical pin layer |

---

# Installation

Place the macro files in the KLayout Python macro directory.

On Linux:

```text
~/.klayout/pymacros/
```

Recommended configuration:

```text
~/.klayout/pymacros/
├── photonics_pdk_v4.lym
└── photonics_router_v5_3_2.lym
```

Older router versions should be moved to another directory to avoid duplicate plugin registration.

After changing the macro files, completely exit KLayout and restart it.

---

# Using the PCell Library

Start KLayout.

From the Instance placement tool, select:

```text
Library
  ↓
Photonics
```

Select the desired PCell, configure its parameters, and place it in the layout.

---

# Using the Photonics Router

The current v5.3.2 workflow is intended to be:

1. Place Photonics PCells in the layout
2. Select `Photonics Router v5.3.2` from the toolbar
3. Click near the first optical port
4. Click near the second optical port
5. Generate the waveguide on Layer `1/0`

The router searches for optical ports on Layer `2/0` and snaps the clicked positions to those ports.

Port-direction detection from Pin Paths is also being developed so that the waveguide endpoint tangents can be aligned with the optical ports.

---

# Repository Structure

```text
klayout-photonics-pdk/
├── README.md
├── README_en.md
├── LICENSE
├── .gitignore
│
├── pymacros/
│   ├── photonics_pdk_v4.lym
│   └── photonics_router_v5_3_2.lym
│
├── docs/
│   ├── specification.md
│   └── KLayout_Silicon_Photonics_PCell_Router_Spec_v0.1.docx
│
├── examples/
└── tests/
```

For detailed specifications, see:

[docs/specification.md](docs/specification.md)

---

# Current Limitations

This project is currently under development.

The following functions and validations are not yet complete:

- Foundry process optimization
- Optical simulation and device-dimension validation
- Exact Euler / Clothoid bends
- Guaranteed minimum bend radius
- DRC-aware routing
- Obstacle avoidance
- Automatic taper insertion
- Automatic port-width inheritance
- Optical path-length matching
- Meander routing
- TE / TM mode information
- Photonic netlist integration

The current PCells should therefore be treated as:

**Geometry PCells for layout development, education, and experimentation.**

---

# Development Roadmap

## v5.4

- Stabilize the port-direction-aware router
- Visualize selected ports
- Display snap status
- Improve router usability

## v5.5

- Minimum-bend-radius-aware routing
- Euler / Arc-based routing
- More natural optical port connections

## v6

- Obstacle avoidance
- DRC-aware routing
- Inherit waveguide width from ports
- Inherit layer information from ports
- Automatic taper insertion

## Future

- Optical Path Length Matching
- MZI Differential Length Control
- Meander Routing
- Photonic Netlist integration
- Circuit connectivity management
- Optical simulator integration
- Process-specific Silicon Photonics PDK support

---

# Project Goal

The long-term goal is to build a Silicon Photonics layout flow in KLayout:

```text
PCell
  ↓
Optical Port
  ↓
Automatic Waveguide Routing
  ↓
DRC
  ↓
Optical Simulation
  ↓
GDS
```

---

# Documentation

Functional specification:

[docs/specification.md](docs/specification.md)

Word specification:

`docs/KLayout_Silicon_Photonics_PCell_Router_Spec_v0.1.docx`

---

# License

This project is released under the **MIT License**.

```text
Copyright (c) 2026 TAKE-HooJoo@SIG
```

The MIT License permits use, modification, distribution, private use, and commercial use subject to the terms of the license.

See [LICENSE](LICENSE) for details.

---

# Disclaimer

This software is provided **AS IS**.

The current PCell dimensions, device geometries, and routing geometries do not guarantee manufacturability, optical performance, or reliability for any specific Silicon Photonics fabrication process.

Before using this project for fabrication, the relevant process design rules, optical models, and simulation results must be independently verified.

---

# Author

**TAKE-HooJoo@SIG**

Open-Source Silicon Photonics PDK / KLayout PCell Development
