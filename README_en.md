# KLayout Silicon Photonics PDK

[日本語](README.md)

An open-source Silicon Photonics PCell library and interactive waveguide router
for **KLayout 0.30.9**.

> **Development status:** Early development / geometry prototype
> This project is not currently a foundry-qualified Silicon Photonics PDK.

## Overview

This project uses KLayout's PCell (Parameterized Cell) framework to generate
basic parametric devices for Silicon Photonics. It also includes a
**Photonics Router** for interactively connecting optical ports defined by
the PCells.

## Supported Environment

- KLayout `0.30.9`
- KLayout Python API
- Linux

# PCell Library v4

Registered library name: `Photonics`

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
| `PortConnector` | Waveguide for optical-port connection |

## PCell Library v4 Example

The following layout was generated with PCell Library v4 on KLayout 0.30.9.
It demonstrates basic geometries including Straight, Bend, Ring,
Directional Coupler, MMI, MZI, and S-bend devices.

![PCell Library v4](images/pcell_library_v4.png)

# Layer Definition

| Purpose | Layer / Datatype |
|---|---|
| Waveguide | `1/0` |
| Optical Pin | `2/0` |

# Photonics Router

Basic operation:

```text
Click start port
       ↓
Click destination port
       ↓
Generate waveguide automatically
```

## Router Development History

| Version | Feature | Status |
|---|---|---|
| v5.1 | Two-click waveguide generation | ✅ Verified on KLayout 0.30.9 |
| v5.2 | Automatic snapping to optical ports | ✅ Verified on KLayout 0.30.9 |
| v5.3 | Port direction recognition | API compatibility issue |
| v5.3.1 | `each_point()` support | Fix in progress |
| v5.3.2 | Optical-port position + direction-aware router | ✅ Verified on KLayout 0.30.9 |
| **v5.4** | **Loop suppression + automatic route-shape adjustment** | **✅ Verified on KLayout 0.30.9** |
| **v5.5** | **Port metadata + waveguide length calculation** | **✅ Verified on KLayout 0.30.9** |

## Router v5.4

**Photonics Router v5.4 has been verified on KLayout 0.30.9.**

v5.4 inherits the port-position and direction recognition introduced in
v5.3.2 while improving cases where Bézier routes could make unnecessarily
large detours or form loop-like paths depending on port placement.

Main improvements:

- Automatic snapping to optical-port positions
- Port direction recognition from Pin Paths
- Automatic control-distance adjustment based on port spacing
- Direction selection based on the relative position of the opposite port
- Detection of excessive detours and fold-back routes
- Fallback routing using intermediate points when necessary
- Smooth tangent connections at the start and end ports
- Waveguide generation on Layer `1/0`

## Photonics Router v5.4 Example

Example operation on KLayout 0.30.9.

### Before Routing

Multiple optical ports are not yet connected.

![Photonics Router v5.4 routing segments](images/router_v5_4_segments.png)

### After Routing

Photonics Router v5.4 recognizes the positions and directions of the optical
ports and creates smooth connections without unnecessary loops.

![Photonics Router v5.4 connected routing](images/router_v5_4_connected.png)

> **Note:** v5.4 is an experimental geometry router with improved loop
> suppression. Strict minimum-bend-radius guarantees, obstacle avoidance,
> DRC-aware routing, and optical path-length matching remain future work.

## Router v5.5

**Photonics Router v5.5 has been verified on KLayout 0.30.9.**

v5.5 inherits the loop suppression and automatic route-shape adjustment of
v5.4 and introduces an `OpticalPort` structure so that optical ports can be
handled as objects with metadata rather than only as coordinates and
directions.

Each `OpticalPort` currently contains:

- Port name
- Position
- Direction
- Waveguide width

v5.5 also calculates the actual path length of the generated Bézier
waveguide and displays the result in micrometers when routing is completed.

Main additions:

- Port metadata management using `OpticalPort`
- Storage of port name / position / direction / width
- Routing using optical-port metadata
- Bézier waveguide path-length calculation
- Waveguide-length output in micrometers
- Routing-completion dialog
- Result output to the Python Console
- Routing behavior inherited from v5.4

### Waveguide Length Verification

Waveguide-length calculation was verified on KLayout 0.30.9.

Straight waveguide:

```text
Waveguide opt3 -> opt5 created
Length = 10.000 um
```

For a test in which the two ports were placed exactly 10.000 µm apart on a
straight line, the calculated waveguide length was also **10.000 µm**.

![Photonics Router v5.5 straight waveguide length](images/router_v5_5_length_straight.png)

Curved waveguide:

```text
Waveguide opt3 -> opt5 created
Length = 10.447 um
```

When the ports were offset vertically and connected with a Bézier curve, the
calculated path length increased to **10.447 µm**, as expected.

![Photonics Router v5.5 curved waveguide length](images/router_v5_5_length_curved.png)

Basic flow:

```text
Optical Port
     ↓
Port Metadata
     ↓
Photonics Router
     ↓
Bézier Waveguide
     ↓
Waveguide Length
```

> **Note:** In v5.5, port names are currently assigned automatically by the
> Router. Reading actual port names defined by PCells, inheriting port width
> and layer metadata, and connection verification are planned for future
> versions.

# Router v5.5 Basic Parameters

| Parameter | Value | Description |
|---|---:|---|
| `WG_WIDTH` | `0.5 µm` | Waveguide width |
| `SNAP_RADIUS` | `4.0 µm` | Optical-port search radius |
| `MIN_LEAD` | `4.0 µm` | Minimum control distance |
| `MAX_LEAD` | `20.0 µm` | Maximum control distance |
| `NPTS` | `96` | Number of Bézier sampling points |
| `WG_LAYER` | `1/0` | Waveguide layer |
| `PIN_LAYER` | `2/0` | Optical-port layer |

# Installation

```text
~/.klayout/pymacros/
├── photonics_pdk_v4.lym
└── photonics_router_v5_5.lym
```

To avoid duplicate registration with older Router versions, move unused
versions outside the `pymacros` directory. Completely close and restart
KLayout after making changes.

# Repository Structure

```text
klayout-photonics-pdk/
├── README.md
├── README_en.md
├── LICENSE
├── images/
│   ├── router_v5_4_connected.png
│   ├── router_v5_4_segments.png
│   ├── router_v5_5_length_curved.png
│   └── router_v5_5_length_straight.png
├── pymacros/
│   ├── photonics_pdk_v4.lym
│   ├── photonics_router_v5_3_2.lym
│   ├── photonics_router_v5_4.lym
│   └── photonics_router_v5_5.lym
├── docs/
├── examples/
└── tests/
```

# Development Roadmap

## v5.5

- Port metadata
- Waveguide length calculation
- Routing result display

**Status: Completed**

## v5.6

- Recognition of port names defined by PCells
- Port width / layer metadata extraction
- Port connection detection
- Unconnected-port detection
- Port width mismatch detection
- Port orientation mismatch detection

## v6.0

- Device recognition
- Connectivity extraction
- Photonic netlist extraction
- Layout verification

## Future

- Minimum-bend-radius-aware routing
- Euler / Arc-based routing
- Obstacle avoidance
- DRC-aware routing
- Automatic taper insertion
- Optical path-length matching

# License

MIT License

```text
Copyright (c) 2026 TAKE-HooJoo@SIG
```

# Disclaimer

This software is provided AS IS. The current PCell dimensions, device
geometries, and routing geometries do not guarantee manufacturability,
optical performance, or reliability for any specific Silicon Photonics
fabrication process.

# Author

**TAKE-HooJoo@SIG**

Open-Source Silicon Photonics PDK / KLayout PCell Development
