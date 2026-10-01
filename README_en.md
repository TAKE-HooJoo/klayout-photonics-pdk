# KLayout Silicon Photonics PDK

[日本語](README.md)

An open-source Silicon Photonics PCell library and interactive waveguide
router for **KLayout 0.30.9**.

> **Development status:** Early development / geometry prototype\
> This project is currently not a foundry-qualified Silicon Photonics
> PDK.

## Overview

This project uses KLayout PCells (Parameterized Cells) to parametrically
generate basic optical devices for Silicon Photonics. It also includes
an interactive **Photonics Router** for connecting optical ports between
PCells with waveguides.

## Supported Environment

-   KLayout `0.30.9`
-   KLayout Python API
-   Linux

# PCell Library v4

Registered library name: `Photonics`

  PCell                  Function
  ---------------------- -----------------------------------
  `Straight`             Straight waveguide
  `Bend90`               90-degree bend
  `EulerBend`            Euler-type bend
  `SBend`                S-bend
  `Ring`                 Ring resonator
  `DirectionalCoupler`   Directional coupler
  `MMI_1x2`              1x2 MMI
  `MZI`                  Mach-Zehnder Interferometer
  `WaveguideRoute`       Bézier-curve waveguide
  `PortConnector`        Optical port connection waveguide

# Layer Definition

  Purpose         Layer / Datatype
  ------------- ------------------
  Waveguide                  `1/0`
  Optical Pin                `2/0`

# Photonics Router

Basic operation:

``` text
Click start port
       ↓
Click destination port
       ↓
Generate waveguide automatically
```

## Router Development History

  -----------------------------------------------------------------------
  Version                 Function                Status
  ----------------------- ----------------------- -----------------------
  v5.1                    Two-click waveguide     ✅ Verified on KLayout
                          generation              0.30.9

  v5.2                    Automatic snapping to   ✅ Verified on KLayout
                          optical port positions  0.30.9

  v5.3                    Port-direction          API compatibility issue
                          detection               

  v5.3.1                  `each_point()` support  Revision continued

  **v5.3.2**              **Optical port          **✅ Verified on
                          position +              KLayout 0.30.9**
                          direction-aware         
                          routing**               
  -----------------------------------------------------------------------

## Router v5.3.2

**Photonics Router v5.3.2 has been verified on KLayout 0.30.9.**

The router obtains optical port positions and directions from Pin Paths
on Layer `2/0`, then generates a smooth waveguide on Layer `1/0` while
taking the source and destination port directions into account.

Basic processing flow:

1.  Click near the first optical port
2.  Search for a Pin Path on Layer `2/0`
3.  Automatically snap to the optical port position
4.  Determine the port direction from the Pin Path
5.  Click near the second optical port
6.  Determine its position and direction
7.  Generate a Bézier curve using both port directions
8.  Create the waveguide on Layer `1/0`

### Verified Functions

-   Interactive two-click routing
-   Optical port search on Layer `2/0`
-   Automatic snapping to optical port positions
-   Port-direction detection from Pin Paths
-   Tangential connection to source and destination port directions
-   Smooth waveguide generation using a cubic Bézier curve
-   Waveguide generation on Layer `1/0`

> **Note:** The current router is an experimental geometry-based router.
> Strict minimum bend-radius guarantees, obstacle avoidance, DRC-aware
> routing, optical path-length matching, and related advanced functions
> are planned for future development.

# Router Parameters

  Parameter            Value Description
  --------------- ---------- -------------------------------------
  `WG_WIDTH`        `0.5 µm` Waveguide width
  `SNAP_RADIUS`     `4.0 µm` Optical port search radius
  `LEAD`            `8.0 µm` Control distance for port direction
  `NPTS`                `80` Number of Bézier curve points
  `WG_LAYER`           `1/0` Waveguide layer
  `PIN_LAYER`          `2/0` Optical pin layer

# Installation

``` text
~/.klayout/pymacros/
├── photonics_pdk_v4.lym
└── photonics_router_v5_3_2.lym
```

After changing the macro files, completely exit KLayout and restart it.

# Development Roadmap

## v5.4

-   Stabilize the port-direction-aware router
-   Visualize selected ports
-   Display snap status
-   Improve router usability

## v5.5

-   Minimum-bend-radius-aware routing
-   Euler / Arc-based routing

## v6

-   Obstacle avoidance
-   DRC-aware routing
-   Inherit waveguide width and layer information from ports
-   Automatic taper insertion

# License

MIT License

``` text
Copyright (c) 2026 TAKE-HooJoo@SIG
```

# Disclaimer

This software is provided **AS IS**. The current PCell dimensions,
device geometries, and routing geometries do not guarantee
manufacturability, optical performance, or reliability for any specific
Silicon Photonics fabrication process.

# Author

**TAKE-HooJoo@SIG**

Open-Source Silicon Photonics PDK / KLayout PCell Development
