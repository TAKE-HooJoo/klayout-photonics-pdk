# KLayout Silicon Photonics PDK

[English](README_en.md)

**KLayout 0.30.9** 向けのオープンソース Silicon Photonics PCell
ライブラリと、対話型導波路ルーターです。

> **開発状況:** 初期開発・ジオメトリプロトタイプ\
> 現時点ではファウンドリ認定済みの Silicon Photonics PDK
> ではありません。

## 概要

KLayout の PCell（Parameterized Cell）機能を利用して、Silicon Photonics
向けの基本的な光デバイスをパラメトリックに生成します。また、PCell
に定義された光ポート間を導波路で接続する **Photonics Router**
を開発しています。

## 対応環境

-   KLayout `0.30.9`
-   KLayout Python API
-   Linux

# PCell Library v4

登録ライブラリ名：`Photonics`

  PCell                  機能
  ---------------------- -----------------------------
  `Straight`             直線導波路
  `Bend90`               90°ベンド
  `EulerBend`            Euler 系ベンド
  `SBend`                S ベンド
  `Ring`                 リング共振器
  `DirectionalCoupler`   方向性結合器
  `MMI_1x2`              1入力2出力 MMI
  `MZI`                  Mach-Zehnder Interferometer
  `WaveguideRoute`       Bézier 曲線による導波路
  `PortConnector`        光ポート接続用導波路

# レイヤ定義

  用途            Layer / Datatype
  ------------- ------------------
  Waveguide                  `1/0`
  Optical Pin                `2/0`

# Photonics Router

基本操作：

``` text
始点ポートをクリック
        ↓
終点ポートをクリック
        ↓
導波路を自動生成
```

## Router 開発履歴

  ------------------------------------------------------------------------------
  Version                 機能                           状態
  ----------------------- ------------------------------ -----------------------
  v5.1                    2クリックによる導波路生成      ✅ KLayout 0.30.9
                                                         動作確認済み

  v5.2                    光ポート位置への自動スナップ   ✅ KLayout 0.30.9
                                                         動作確認済み

  v5.3                    ポート方向認識                 API互換性問題

  v5.3.1                  `each_point()` 対応            修正継続

  **v5.3.2**              **光ポート位置＋方向認識       **✅ KLayout 0.30.9
                          Router**                       動作確認済み**
  ------------------------------------------------------------------------------

## Router v5.3.2

**Photonics Router v5.3.2 は KLayout 0.30.9 で動作確認済みです。**

Layer `2/0` の Pin Path
から光ポートの位置と方向を取得し、始点・終点の方向を考慮した滑らかな導波路を
Layer `1/0` に生成します。

基本処理：

1.  1つ目の光ポート付近をクリック
2.  Layer `2/0` の Pin Path を探索
3.  光ポート位置へ自動スナップ
4.  Pin Path からポート方向を取得
5.  2つ目の光ポート付近をクリック
6.  同様に位置と方向を取得
7.  両ポートの方向を考慮した Bézier 曲線を生成
8.  Layer `1/0` に導波路を生成

### 現在確認済みの機能

-   2クリックによる対話型ルーティング
-   Layer `2/0` の光ポート探索
-   光ポート位置への自動スナップ
-   Pin Path からのポート方向認識
-   始点・終点ポート方向への接線接続
-   Cubic Bézier 曲線による滑らかな導波路生成
-   Layer `1/0` への導波路生成

> **Note:**
> 現在のルーターはジオメトリベースの実験的ルーターです。最小曲げ半径の厳密な保証、障害物回避、DRC-aware
> routing、光路長マッチングなどは今後実装予定です。

# Router の基本パラメータ

  Parameter            Value 内容
  --------------- ---------- ------------------------------
  `WG_WIDTH`        `0.5 µm` 導波路幅
  `SNAP_RADIUS`     `4.0 µm` 光ポート探索範囲
  `LEAD`            `8.0 µm` ポート方向を維持する制御距離
  `NPTS`                `80` Bézier 曲線の分割点数
  `WG_LAYER`           `1/0` 導波路レイヤ
  `PIN_LAYER`          `2/0` 光ポートレイヤ

# インストール

``` text
~/.klayout/pymacros/
├── photonics_pdk_v4.lym
└── photonics_router_v5_3_2.lym
```

変更後は KLayout を完全終了して再起動してください。

# 開発ロードマップ

## v5.4

-   ポート方向認識 Router の安定化
-   選択ポートの可視化
-   Snap 状態の表示
-   Router 操作性の改善

## v5.5

-   最小曲げ半径を考慮した Router
-   Euler / Arc ベースのルーティング

## v6

-   障害物回避
-   DRC-aware routing
-   ポートから導波路幅・Layer 情報を継承
-   自動テーパ挿入

# ライセンス

MIT License

``` text
Copyright (c) 2026 TAKE-HooJoo@SIG
```

# 注意事項

本ソフトウェアは現状のまま（AS IS）提供されます。現在の PCell
寸法、デバイス形状およびルーティング形状は、特定の Silicon Photonics
製造プロセスに対する製造可能性、光学性能、信頼性を保証するものではありません。

# Author

**TAKE-HooJoo@SIG**

Open-Source Silicon Photonics PDK / KLayout PCell Development
