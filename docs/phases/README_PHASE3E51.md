# Phase 3E-5.1: waypoint kink diagnosis and experimental fillet

This is a **diagnostic/experimental** first iteration, not proof of photonic bend DRC.
Existing v2 router and GDS exporter are unchanged.

## Install

```sh
cd ~/Photonics/klayout-photonics-pdk
unzip -n ~/Downloads/klayout_phase3e51_continuity.zip -d .
python3 -m unittest discover -s tests -p 'test_route_continuity.py' -v
klayout -b -r tests/test_klayout_smooth_waypoint.py
```

The KLayout test **passes** if the smoothed route is safe under the implemented checks **or if the experimental smoothing fails closed with an explicit reason**. It does not guarantee that the original 82.056 um route becomes smooth. This is deliberate: the current waypoint router joins sampled CSC legs and filleting every sampled vertex is not generally geometrically feasible.

## Limitations / next step

- The fillet module uses exact-radius circular arcs at polyline vertices and checks shared straight lead availability. It does not solve global route optimization.
- Sampled arcs from the CSC router are polygonal approximations. `min_radius(points)` is only a discrete diagnostic, not a proof of continuous curvature.
- The v3 wrapper currently fillets vertices whose discrete turn exceeds the tolerance. It may reject valid routes due to insufficient lead; a better approach is to construct tangent-matched CSC/CSCSC waypoint segments from the outset.
- Full self-spacing DRC, global obstacle clearance after GDS quantization, and foundry signoff are not provided.
- Do not use the experimental v3 wrapper for tapeout without additional checks.
