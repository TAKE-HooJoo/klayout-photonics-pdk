# KLayout Silicon Photonics PDK

[English](README_en.md)

**KLayout 0.30.9** 向けのオープンソース Silicon Photonics PCell ライブラリと、対話型導波路ルーターです。

> **開発状況:** 初期開発・ジオメトリプロトタイプ  
> 現時点ではファウンドリ認定済みの Silicon Photonics PDK ではありません。

---

## 概要

このプロジェクトでは、KLayout の PCell（Parameterized Cell）機能を利用して、Silicon Photonics 向けの基本的な光デバイスをパラメトリックに生成します。

また、PCell に定義された光ポートを指定して、デバイス間を導波路で接続する **Photonics Router** を開発しています。

主な目的は以下です。

- KLayout による Silicon Photonics レイアウトの学習・実験
- PCell による光デバイスのパラメトリック生成
- 光ポートを利用した導波路ルーティング
- オープンソース Silicon Photonics PDK の開発
- Silicon Photonics レイアウト技術の教育
- KLayout Python API を利用した Photonics CAD 機能の検討

---

## 対応環境

現在、以下の環境で開発・評価しています。

- KLayout `0.30.9`
- KLayout Python API
- Linux

KLayout のバージョンによって Python API の仕様が異なる場合があるため、他のバージョンでは一部機能が動作しない可能性があります。

---

# PCell Library

## PCell Library v4

KLayout への登録ライブラリ名：

`Photonics`

現在、以下の10種類の PCell を実装しています。

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

---

## Straight

直線導波路を生成します。

主なパラメータ：

- Length
- Width

導波路の両端には光ポートを生成します。

---

## Bend90

90°曲げ導波路を生成します。

光回路内で導波路の方向を90°変更するために使用します。

---

## EulerBend

曲率を滑らかに変化させる Euler 系ベンドです。

現在の実装はジオメトリ検討用の近似実装であり、厳密な Clothoid / Euler 曲線を保証するものではありません。

---

## SBend

2つの異なる位置の導波路を滑らかに接続する S 字型導波路です。

デバイス間の光ポート位置調整などに使用できます。

---

## Ring

リング共振器の基本形状を生成します。

リング導波路とバス導波路から構成されます。

---

## DirectionalCoupler

2本の導波路を近接させた方向性結合器を生成します。

アクセス部分には滑らかな S ベンドを使用しています。

---

## MMI_1x2

1入力・2出力の MMI（Multi-Mode Interferometer）を生成します。

基本構成：

- 1入力ポート
- MMI 本体
- 2出力ポート

---

## MZI

Mach-Zehnder Interferometer を生成します。

基本構成：

- 入力 MMI
- 2本の光導波路アーム
- 出力 MMI
- 分離・再結合用 S ベンド

現在は基本的なジオメトリ生成を目的としています。

---

## WaveguideRoute

始点と終点の相対位置から、滑らかな導波路を生成します。

主なパラメータ：

- `dx`
- `dy`
- `width`
- `radius`

現在は Cubic Bézier 曲線を使用しています。

`radius` は曲線形状を決めるための補助パラメータであり、厳密な最小曲げ半径を保証するものではありません。

---

## PortConnector

光ポート接続用の短い直線導波路を生成します。

両端に、

- `opt1`
- `opt2`

の光ポートを生成します。

---

# 光ポート

光ポート情報は Layer `2/0` に生成します。

基本的なポート名：

```text
opt1
opt2
opt3
...
```

光ポートは、

- ポート位置
- ポート名
- 接続方向

を表現するために使用します。

短い Pin Path を配置することで、Photonics Router がポートの位置と方向を認識できる構造を目指しています。

---

# レイヤ定義

現在の基本レイヤは以下です。

| 用途 | Layer / Datatype |
|---|---:|
| Waveguide | `1/0` |
| Optical Pin | `2/0` |

### Layer 1/0

Silicon Photonics の導波路形状を配置します。

### Layer 2/0

光ポート情報を配置します。

主に、

- Pin Path
- `opt1`
- `opt2`

などのポート情報に使用します。

---

# Photonics Router

PCell 間を光導波路で接続する対話型ルーターを開発しています。

基本的な操作コンセプトは、

```text
始点ポートをクリック
        ↓
終点ポートをクリック
        ↓
導波路を自動生成
```

です。

---

## Router 開発履歴

| Version | 機能 | 状態 |
|---|---|---|
| v5.1 | 2クリックによる導波路生成 | 動作確認済み |
| v5.2 | 光ポート位置への自動スナップ | 動作確認済み |
| v5.3 | ポート方向認識 | API互換性問題 |
| v5.3.1 | `each_point()` 対応 | 修正継続 |
| v5.3.2 | 位置＋方向認識 Router の再構築 | 動作確認中 |

---

## Router v5.1

最初の対話型 Router です。

2点をクリックすると、その2点を接続する導波路を生成します。

```text
Click 1
   ↓
Click 2
   ↓
Waveguide
```

---

## Router v5.2

光ポートへの自動スナップ機能を追加しました。

クリック位置の近くに Layer `2/0` の光ポートが存在する場合、そのポート位置へ自動的にスナップします。

これにより、PCell の光ポートと導波路を正確に接続しやすくなります。

---

## Router v5.3.x

光ポートの位置だけでなく、**ポート方向**も認識して導波路を生成する機能を開発しています。

目的は、導波路の端部を光ポートの方向に自然に接続することです。

Layer `2/0` の Pin Path から方向ベクトルを取得し、導波路端部の接線方向へ反映します。

---

## Router v5.3.2

KLayout 0.30.9 の Python API に合わせて、ポート方向認識部分を再構築したバージョンです。

主な処理：

1. 1つ目の光ポート付近をクリック
2. Layer `2/0` の Pin Path を探索
3. 光ポート位置へスナップ
4. Pin Path からポート方向を取得
5. 2つ目の光ポートをクリック
6. 同様に位置と方向を取得
7. 両ポートの方向を考慮した曲線を生成
8. Layer `1/0` に導波路を生成

現在、KLayout 0.30.9 上で動作確認を進めています。

---

# Router の基本パラメータ

現在の v5.3.2 では、以下の値を使用しています。

| Parameter | Value | 内容 |
|---|---:|---|
| `WG_WIDTH` | `0.5 µm` | 導波路幅 |
| `SNAP_RADIUS` | `4.0 µm` | 光ポート探索範囲 |
| `LEAD` | `8.0 µm` | ポート方向を維持する制御距離 |
| `NPTS` | `80` | Bézier 曲線の分割点数 |
| `WG_LAYER` | `1/0` | 導波路レイヤ |
| `PIN_LAYER` | `2/0` | 光ポートレイヤ |

---

# インストール

KLayout の Python Macro ディレクトリへファイルを配置します。

Linux の場合：

```text
~/.klayout/pymacros/
```

現在の推奨構成：

```text
~/.klayout/pymacros/
├── photonics_pdk_v4.lym
└── photonics_router_v5_3_2.lym
```

古い Router を同時に配置すると Plugin が重複登録される可能性があります。

使用しない旧バージョンは別のディレクトリへ退避してください。

ファイルを変更した後は、KLayout を完全終了して再起動します。

---

# PCell の使用方法

KLayout を起動します。

Instance 配置から、

```text
Library
  ↓
Photonics
```

を選択します。

使用する PCell を選択し、パラメータを設定してレイアウトへ配置します。

---

# Photonics Router の使用方法

現在開発中の v5.3.2 では、以下の操作を想定しています。

1. Photonics PCell をレイアウトへ配置
2. ツールバーから `Photonics Router v5.3.2` を選択
3. 1つ目の光ポート付近をクリック
4. 2つ目の光ポート付近をクリック
5. Layer `1/0` に導波路を生成

Router は Layer `2/0` の光ポートを探索し、クリック位置を光ポートへスナップします。

さらに Pin Path からポート方向を取得し、導波路端部の接線方向を合わせる機能を開発しています。

---

# リポジトリ構成

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

詳細仕様については、

[docs/specification.md](docs/specification.md)

を参照してください。

---

# 現在の制約

このプロジェクトは現在開発段階です。

以下の機能・検証はまだ完了していません。

- ファウンドリプロセスへの最適化
- 光学シミュレーションによるデバイス寸法検証
- 厳密な Euler / Clothoid ベンド
- 最小曲げ半径保証
- DRC-aware routing
- 障害物回避
- 自動テーパ挿入
- ポート幅の自動継承
- 光路長マッチング
- Meander routing
- TE / TM モード情報
- Photonic Netlist との連携

そのため、現在の PCell は、

**レイアウト開発・教育・実験用途のジオメトリ PCell**

として扱ってください。

---

# 開発ロードマップ

## v5.4

- ポート方向認識 Router の安定化
- 選択ポートの可視化
- Snap 状態の表示
- Router 操作性の改善

## v5.5

- 最小曲げ半径を考慮した Router
- Euler / Arc ベースのルーティング
- より自然な光ポート接続

## v6

- 障害物回避
- DRC-aware routing
- ポートから導波路幅を継承
- ポートから Layer 情報を継承
- 自動テーパ挿入

## 将来

- Optical Path Length Matching
- MZI Differential Length Control
- Meander Routing
- Photonic Netlist との連携
- 回路接続情報の管理
- 光学シミュレータとの連携
- プロセス固有 Silicon Photonics PDK への展開

---

# 今後の目標

最終的には、

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

という一連の Silicon Photonics レイアウトフローを、KLayout 上で構築することを目標としています。

---

# ドキュメント

機能仕様書：

[docs/specification.md](docs/specification.md)

Word 版仕様書：

`docs/KLayout_Silicon_Photonics_PCell_Router_Spec_v0.1.docx`

---

# ライセンス

このプロジェクトは **MIT License** で公開しています。

```text
Copyright (c) 2026 TAKE-HooJoo@SIG
```

個人利用、研究用途、教育用途、企業利用、改造、再配布、商用利用が可能です。

詳細については [LICENSE](LICENSE) を参照してください。

---

# 注意事項

本ソフトウェアは現状のまま（AS IS）提供されます。

現在の PCell 寸法、デバイス形状およびルーティング形状は、特定の Silicon Photonics 製造プロセスに対して、製造可能性、光学性能、信頼性を保証するものではありません。

実際の製造に使用する場合は、対象プロセスの設計ルール、光学モデル、シミュレーション結果などを別途確認する必要があります。

---

# Author

**TAKE-HooJoo@SIG**

Open-Source Silicon Photonics PDK / KLayout PCell Development