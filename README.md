# KLayout Silicon Photonics PDK

[English](README_en.md)

**KLayout 0.30.9** 向けのオープンソース Silicon Photonics PCell
ライブラリと、対話型導波路ルーターです。

> **開発状況:** 初期開発・ジオメトリプロトタイプ
> 現時点ではファウンドリ認定済みの Silicon Photonics PDK
> ではありません。

## 概要

KLayout の PCell（Parameterized Cell）機能を利用して、Silicon Photonics
向けの基本的な光デバイスをパラメトリックに生成します。また、PCell
に定義された光ポート間を導波路で接続する **Photonics Router**
を開発しています。

## 対応環境

- KLayout `0.30.9`
- KLayout Python API
- Linux

# PCell Library v4

登録ライブラリ名：`Photonics`

| PCell | 機能 |
|---|---|
| `Straight` | 直線導波路 |
| `Bend90` | 90°ベンド |
| `EulerBend` | Euler 系ベンド |
| `SBend` | S ベンド |
| `Ring` | リング共振器 |
| `DirectionalCoupler` | 方向性結合器 |
| `MMI_1x2` | 1入力2出力 MMI |
| `MZI` | Mach-Zehnder Interferometer |
| `WaveguideRoute` | Bézier 曲線による導波路 |
| `PortConnector` | 光ポート接続用導波路 |

## PCell Library v4 動作例

KLayout 0.30.9 上で生成した PCell Library v4
のレイアウト例です。Straight、Bend、Ring、Directional
Coupler、MMI、MZI、S-bend などの基本ジオメトリを確認できます。

![PCell Library v4](images/pcell_library_v4.png)

# レイヤ定義

| 用途 | Layer / Datatype |
|---|---|
| Waveguide | `1/0` |
| Optical Pin | `2/0` |

# Photonics Router

基本操作：

```text
始点ポートをクリック
       ↓
終点ポートをクリック
       ↓
導波路を自動生成
```

## Router 開発履歴

| Version | 機能 | 状態 |
|---|---|---|
| v5.1 | 2クリックによる導波路生成 | ✅ KLayout 0.30.9 動作確認済み |
| v5.2 | 光ポート位置への自動スナップ | ✅ KLayout 0.30.9 動作確認済み |
| v5.3 | ポート方向認識 | API互換性問題 |
| v5.3.1 | `each_point()` 対応 | 修正継続 |
| v5.3.2 | 光ポート位置＋方向認識 Router | ✅ KLayout 0.30.9 動作確認済み |
| **v5.4** | **ループ抑制＋経路形状の自動調整** | **✅ KLayout 0.30.9 動作確認済み** |
| **v5.5** | **Port metadata＋導波路長計算** | **✅ KLayout 0.30.9 動作確認済み** |

## Router v5.4

**Photonics Router v5.4 は KLayout 0.30.9 で動作確認済みです。**

v5.3.2 のポート位置・方向認識を継承しつつ、ポート配置によって Bézier
曲線が不要に大回りしたりループ状になったりする問題を改善しました。

主な改善点：

- 光ポート位置への自動スナップ
- Pin Path からのポート方向認識
- ポート間距離に応じた制御距離の自動調整
- 相手ポートとの位置関係を考慮した方向選択
- 過大な迂回・折り返しの検出
- 必要に応じた中間点を使うフォールバック経路
- 始点・終点での滑らかな接線接続
- Layer `1/0` への導波路生成

## Photonics Router v5.4 動作例

KLayout 0.30.9 での動作例です。

### ルーティング前

複数の光ポートが未接続の状態です。

![Photonics Router v5.4 routing segments](images/router_v5_4_segments.png)

### ルーティング後

Photonics Router v5.4
が光ポートの位置と方向を認識し、不要なループを発生させず滑らかに接続します。

![Photonics Router v5.4 connected routing](images/router_v5_4_connected.png)

> **Note:** v5.4
> はループ抑制を改善した実験的ジオメトリルーターです。厳密な最小曲げ半径保証、障害物回避、DRC-aware
> routing、光路長マッチングは今後の課題です。

## Router v5.5

**Photonics Router v5.5 は KLayout 0.30.9 で動作確認済みです。**

v5.4 のループ抑制・経路形状自動調整を継承しつつ、
光ポートを単なる座標と方向ではなく、metadata を持つ
`OpticalPort` として扱う構造を導入しました。

各 `OpticalPort` は現在、以下の情報を保持します。

- Port name
- Position
- Direction
- Waveguide width

また、生成した Bézier 導波路の経路長を計算し、
ルーティング完了時に µm 単位で表示します。

主な追加機能：

- `OpticalPort` による Port metadata 管理
- Port name / position / direction / width の保持
- Port metadata を利用したルーティング
- Bézier 導波路の経路長計算
- Waveguide length の µm 表示
- Routing 完了ダイアログ
- Python Console への結果出力
- v5.4 のルーティングアルゴリズムを継承

### Waveguide Length 動作確認

KLayout 0.30.9 上で導波路長計算を確認しました。

直線導波路：

```text
Waveguide opt3 -> opt5 created
Length = 10.000 um
```

Port 間を直線で 10.000 µm 離して配置したテストでは、
計算結果も **10.000 µm** となることを確認しました。

曲線導波路：

```text
Waveguide opt3 -> opt5 created
Length = 10.447 um
```

Port を上下方向にもずらして Bézier 曲線を生成した場合、
直線接続より長い **10.447 µm** が得られることを確認しました。

基本フロー：

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

> **Note:** v5.5 の Port name は現在 Router が自動的に付与しています。
> PCell に定義された実際の Port name の取得、Port width / Layer の継承、
> 接続検証は今後の拡張予定です。

# Router v5.5 の基本パラメータ

| Parameter | Value | 内容 |
|---|---:|---|
| `WG_WIDTH` | `0.5 µm` | 導波路幅 |
| `SNAP_RADIUS` | `4.0 µm` | 光ポート探索範囲 |
| `MIN_LEAD` | `4.0 µm` | 最小制御距離 |
| `MAX_LEAD` | `20.0 µm` | 最大制御距離 |
| `NPTS` | `96` | Bézier 曲線の分割点数 |
| `WG_LAYER` | `1/0` | 導波路レイヤ |
| `PIN_LAYER` | `2/0` | 光ポートレイヤ |

# インストール

```text
~/.klayout/pymacros/
├── photonics_pdk_v4.lym
└── photonics_router_v5_5.lym
```

旧Routerとの重複登録を避ける場合は、使用しない旧バージョンを `pymacros`
外へ移動してください。変更後は KLayout を完全終了して再起動します。

# リポジトリ構成

```text
klayout-photonics-pdk/
├── README.md
├── README_en.md
├── LICENSE
├── images/
│   ├── router_v5_4_connected.png
│   └── router_v5_4_segments.png
├── pymacros/
│   ├── photonics_pdk_v4.lym
│   ├── photonics_router_v5_3_2.lym
│   ├── photonics_router_v5_4.lym
│   └── photonics_router_v5_5.lym
├── docs/
├── examples/
└── tests/
```

# 開発ロードマップ

## v5.5

- Port metadata
- Waveguide length calculation
- Routing result display

**Status: Completed**

## v5.6

- PCell に定義された Port name の認識
- Port width / Layer metadata の取得
- Port connection detection
- Unconnected port の検出
- Port width mismatch の検出
- Port orientation mismatch の検出

## v6.0

- Device recognition
- Connectivity extraction
- Photonic netlist extraction
- Layout verification

## Future

- 最小曲げ半径を考慮した Router
- Euler / Arc ベースのルーティング
- 障害物回避
- DRC-aware routing
- 自動テーパ挿入
- Optical path length matching

# ライセンス

MIT License

```text
Copyright (c) 2026 TAKE-HooJoo@SIG
```

# 注意事項

本ソフトウェアは現状のまま（AS IS）提供されます。現在の PCell
寸法、デバイス形状およびルーティング形状は、特定の Silicon Photonics
製造プロセスに対する製造可能性、光学性能、信頼性を保証するものではありません。

# Author

**TAKE-HooJoo@SIG**

Open-Source Silicon Photonics PDK / KLayout PCell Development
