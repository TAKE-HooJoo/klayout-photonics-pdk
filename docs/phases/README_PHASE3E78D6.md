# Phase 3E-7.8D-6 — 曲率勾配とCSC理想ジャンプの分離評価

既存のRouter、AUTO_QUALITY、トップのREADMEは変更しません。

## 目的

- 固定物理窓の曲率推定値に対し `max |Δκ/Δs|`（µm⁻²）とRMS勾配を算出する。
- CSC（LSL/RSR/LSR/RSL）の理想的な直線・円弧接続の曲率ジャンプ `1/R`（µm⁻¹）を**別列**に記録する。
- Euler等の解析的なジャンプ情報が無い経路は `N/A` とし、0とは見なさない。

**注意:** `max_abs_window_gradient_inv_um2` は固定窓で平滑化された折れ線の曲率勾配であり、真の点wise `dκ/ds` ではありません。`ideal_csc_line_arc_jump_inv_um` はトポロジーと設計半径に基づく理想値で、実レイアウトの不連続点を検出した値ではありません。光損失の予測にも使えません。

## 導入

既存のPhase D-5が必要です。以下をリポジトリのルートで実行します。

```bash
unzip -o ~/Downloads/Phase3E_7_8D6_Curvature_Gradient.zip
python3 tests/test_curvature_gradient.py
python3 tools/analyze_curvature_gradient.py
```

入力: `tests/phase3e78d4_output/route_centerlines.csv`（D-4で生成）

出力: `tests/phase3e78d6_output/curvature_gradient_sweep.csv`

次段階: 経路の解析的な直線・円弧境界情報をRouterからエクスポートし、理想ジャンプの有無と位置を照合する。窓幅を変えた感度解析も行う。
