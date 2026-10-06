# KLayout Silicon Photonics PDK

[English](README_en.md)

**KLayout 0.30.9** 向けのオープンソース Silicon Photonics PCell
ライブラリと、対話型導波路ルーターです。

> **開発状況:** 初期開発・ジオメトリプロトタイプ
> 現時点ではファウンドリ認定済みの Silicon Photonics PDK ではありません。

## 概要

KLayout の PCell（Parameterized Cell）機能を利用して、Silicon Photonics
向けの基本的な光デバイスをパラメトリックに生成します。また、PCell
に定義された光ポート間を導波路で接続する **Photonics Router** を開発しています。

現在の Router v6.1 では、v6.0 の Photonic Netlist Extraction を継承し、
`PhotonicDevice`、`OpticalPort`、`PhotonicNet` の明示的なデータモデルを導入しています。
PCell のポート名、インスタンス、接続関係、導波路長を認識し、レイアウトから
基本的な Photonic Netlist を抽出できます。

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
       ↓
接続情報・光路長を抽出
```

## Router 開発履歴

| Version | 主な機能 | 状態 |
|---|---|---|
| v5.1 | 2クリックによる導波路生成 | ✅ KLayout 0.30.9 動作確認済み |
| v5.2 | 光ポート位置への自動スナップ | ✅ KLayout 0.30.9 動作確認済み |
| v5.3 | ポート方向認識 | API互換性問題 |
| v5.3.1 | `each_point()` 対応 | 修正版 |
| v5.3.2 | 光ポート位置＋方向認識 | ✅ KLayout 0.30.9 動作確認済み |
| v5.4 | ループ抑制＋経路形状の自動調整 | ✅ KLayout 0.30.9 動作確認済み |
| v5.5 | Port metadata＋Waveguide length | ✅ KLayout 0.30.9 動作確認済み |
| v5.6 | Connectivity verification | ✅ KLayout 0.30.9 動作確認済み |
| v6.0 | Photonic Netlist Extraction | ✅ KLayout 0.30.9 動作確認済み |
| **v6.1** | **Photonic Data Model** | **✅ KLayout 0.30.9 動作確認済み** |

## Router v5.4

v5.4 では、ポート位置・方向認識を継承しながら、Bézier 曲線が不要に
大回りしたりループ状になったりする問題を改善しました。

![Photonics Router v5.4 routing segments](images/router_v5_4_segments.png)

![Photonics Router v5.4 connected routing](images/router_v5_4_connected.png)

## Router v5.5
Connections: 2
Connected ports: 4
Unconnected ports: 4
```

![Photonics Router v5.6 two nets](images/router_v5_6_two_nets.png)

# Photonics Router v6.0

**Photonics Router v6.0 は KLayout 0.30.9 で動作確認済みです。**

v6.0 では、レイアウト上のPCell、Native Port、インスタンス、導波路接続を
解析して基本的な Photonic Netlist を生成します。

主な機能：

- Device recognition
- Instance identification
- Native PCell port name recognition
- Connection extraction
- `PhotonicNet` オブジェクト
- Connected / Unconnected port detection
- NetごとのWaveguide length
- Photonic Netlist表示

出力例：

```text
DEVICES
  DEVICE DirectionalCoupler[1] TYPE DirectionalCoupler
  DEVICE MMI_1x2[1] TYPE MMI_1x2
  DEVICE Ring[1] TYPE Ring

NETLIST
  NET NET1
    PORT DirectionalCoupler[1].opt3
    PORT DirectionalCoupler[2].opt1
    LENGTH 10.621 um

  NET NET3
    PORT MMI_1x2[1].opt2
    PORT Ring[1].opt1
    LENGTH 14.504 um
```

DirectionalCoupler、MMI、Ring を含む異種PCell間でもDevice / Port /
Connection / Lengthを抽出できることを確認しています。

![Photonics Router v6.0 photonic netlist](images/router_v6_0_netlist.png)

## v6.0 データフロー

```text
Layout
  ↓
Device Recognition
  ↓
Native PCell Port Recognition
  ↓
Instance Identification
  ↓
Connection Extraction
  ↓
PhotonicNet
  ↓
Photonic Netlist
```

# Photonics Router v6.1 — Photonic Data Model

**Photonics Router v6.1 は KLayout 0.30.9 で動作確認済みです。**

v6.1 では v6.0 のルーティング動作と Photonic Netlist Extraction を維持しながら、
光回路の内部表現を明示的なデータモデルとして整理しました。

```text
PhotonicDevice
      |
      +-- OpticalPort
               |
               +-- PhotonicNet
```

主な追加点：

- `PhotonicDevice` オブジェクトを追加
- `PhotonicDevice <-> OpticalPort` の関連付け
- `OpticalPort <-> PhotonicNet` の関連付け
- Native PCell port metadata を維持
- Photonic Netlist extraction を維持
- Waveguide length extraction を維持
- v6.0 の2クリック対話型ルーティング動作を維持

動作確認例：

```text
DEVICES
  DEVICE SBend[1] TYPE SBend
  DEVICE SBend[2] TYPE SBend

NETLIST
  NET NET1
    PORT SBend[1].opt2
    PORT SBend[2].opt1
    LENGTH 13.100 um

UNCONNECTED
  -- SBend[1].opt1
  -- SBend[2].opt2
```

このデータモデルは、v6.2 の Bend-aware Router、Photonic Verification、
Netlist Export へ発展させるための基盤です。

![Photonics Router v6.1 Photonic Data Model](images/router_v6_1_photonic_data_model.png)

# Router 基本パラメータ

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
└── photonics_router_v6_1.lym
```

旧Routerとの重複登録を避ける場合は、使用しない旧バージョンを
`pymacros` 外へ移動してください。変更後は KLayout を完全終了して再起動します。

# リポジトリ構成

```text
klayout-photonics-pdk/
├── README.md
├── README_en.md
├── LICENSE
├── images/
│   ├── router_v5_4_connected.png
│   ├── router_v5_4_segments.png
│   ├── router_v5_5_length_curved.png
│   ├── router_v5_5_length_straight.png
│   ├── router_v5_5_1_native_ports.png
│   ├── router_v5_5_2_instance_ports.png
│   ├── router_v5_6_connectivity.png
│   ├── router_v5_6_two_nets.png
│   ├── router_v6_0_netlist.png
│   └── router_v6_1_photonic_data_model.png
├── pymacros/
│   ├── photonics_pdk_v4.lym
│   ├── photonics_router_v5_3_2.lym
│   ├── photonics_router_v5_4.lym
│   ├── photonics_router_v5_5.lym
│   ├── photonics_router_v5_6.lym
│   └── photonics_router_v6_1.lym
├── docs/
├── examples/
└── tests/
```

# 開発ロードマップ

## v6.0 — Photonic Netlist Extraction

- Device recognition
- Instance identification
- Native port recognition
- Connectivity extraction
- Photonic Netlist extraction

**Status: Completed (prototype)**

## v6.1 — Photonic Data Model

- `PhotonicDevice`
- `OpticalPort`
- `PhotonicNet`
- Device / Port / Net relationship

**Status: Completed — KLayout 0.30.9 verified**

## v6.2 — Bend-aware Router

- Minimum bend radius
- Curvature check
- Bézier route optimization

**Status: Next**

## v6.3 — Photonic Verification

- Unconnected port detection
- Port width mismatch detection
- Port orientation mismatch detection
- Bend-radius violation detection

## v6.4 — Netlist Export

- Photonic netlist file export

## v7.0 — Advanced Router

- Euler / Clothoid bend
- Waveguide types
- Advanced routing
