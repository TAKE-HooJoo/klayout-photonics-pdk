# Phase 3E-7.8A — Euler S-Bend vs CSC 曲率比較

既存の Hybrid Router v6.5 を変更せず、同じポート `(0,0)` → `(80,15)` µm（始点 outward `(1,0)`、終点 outward `(-1,0)`）で AUTO と CSC を比較します。

## 導入

リポジトリのルートでZIPを展開し、次を実行してください。

```bash
klayout -b -r tests/test_route_curvature_compare_v65.py
```

出力先: `tests/phase3e78a_output/`

- `summary.csv` — 経路長、サンプリング半径、最大絶対曲率など
- `auto_curvature.csv` / `csc_curvature.csv` — 弧長と符号付き離散曲率
- `auto.gds` / `csc.gds` — 同じ条件のGDS

## 注意

曲率は隣接3点の外接円に基づく離散近似です。点間隔やポリライン化の影響を受けます。`max_neighbor_delta_k_per_um`は隣接サンプルの曲率差であり、**曲率微分 dκ/ds ではありません**。異なるサンプリング密度の経路間でこの値を単純に優劣比較しないでください。Euler/CSCの真の接続部の曲率連続性や光学損失をこのテストだけで証明することはできません。
