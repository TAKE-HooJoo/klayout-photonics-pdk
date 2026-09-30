# KLayout Silicon Photonics PDK

[English](README_en.md)

**KLayout 0.30.9** 向けのオープンソース Silicon Photonics PCell ライブラリと、対話型導波路ルーターです。

> **開発状況:** 初期開発・ジオメトリプロトタイプ  
> 現時点ではファウンドリ認定済みのPhotonics PDKではありません。

## 概要

このプロジェクトでは、KLayoutのPCell機能を利用して、Silicon Photonics向けの基本的な光デバイスを生成します。

また、光ポートを指定してPCell間を導波路で接続する **Photonics Router** を開発しています。

主な目的：

- KLayoutによるSilicon Photonicsレイアウトの学習・実験
- PCellによる光デバイスのパラメトリック生成
- 光ポートを利用した導波路ルーティング
- オープンソースPhotonics PDKの開発
- Silicon Photonicsレイアウト技術の教育

## PCell Library v4

KLayout登録ライブラリ名：`Photonics`

現在、以下の10種類のPCellを実装しています。

| PCell | 機能 |
|---|---|
| `Straight` | 直線導波路 |
| `Bend90` | 90°ベンド |
| `EulerBend` | Euler系ベンド |
| `SBend` | Sベンド |
| `Ring` | リング共振器 |
| `DirectionalCoupler` | 方向性結合器 |
| `MMI_1x2` | 1入力2出力 MMI |
| `MZI` | Mach-Zehnder Interferometer |
| `WaveguideRoute` | Bézier曲線による導波路 |
| `PortConnector` | ポート接続用導波路 |

## Photonics Router

PCell間を接続する対話型導波路ルーターを開発しています。

| Version | 機能 | 状態 |
|---|---|---|
| v5.1 | 2クリックによる導波路生成 | 動作確認済み |
| v5.2 | 光ポート位置への自動スナップ | 動作確認済み |
| v5.3 | ポート方向認識 | API互換性問題 |
| v5.3.1 | `each_point()` 対応 | 修正継続 |
| v5.3.2 | 位置＋方向認識Router再構築 | 動作確認中 |

## レイヤ定義

| 用途 | Layer / Datatype |
|---|---:|
| Waveguide | `1/0` |
| Optical Pin | `2/0` |

光ポートには `opt1`, `opt2`, ... の名称を使用します。

## インストール

KLayoutのPython Macroディレクトリへファイルを配置します。

```text
~/.klayout/pymacros/
├── photonics_pdk_v4.lym
└── photonics_router_v5_3_2.lym