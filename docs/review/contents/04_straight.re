= Straight — 直線導波路

@<b>{実装基準}：@<tt>{pymacros/photonics_pdk_v4.lym} (https://github.com/TAKE-HooJoo/klayout-photonics-pdk/blob/main/pymacros/photonics_pdk_v4.lym) の @<tt>{Straight} クラス（ソース39–47行付近）。以下のソースは可読性のため改行・整形しています。@<tt>{main} ブランチは更新されるため、正式公開時は対象コミットを固定してください。

== 概要と用途

@<tt>{Straight} は、幅が一定の直線光導波路を生成する基本PCellです。光回路内でデバイス間を接続するほか、光路長の調整、レイアウト検証、光ポート認識の動作確認に利用できます。

本PCellは@<b>{導波路の幾何学形状}を生成します。伝搬損失・実効屈折率・群屈折率などを自動計算するものではありません。

== 構造と座標

//emlist[text]{
                      length = L
          x = 0                         x = L
             │                            │
  opt1       ●════════════════════════════●       opt2
             │       width = w            │
             └──────── y = 0 ─────────────┘

  中心線： (0, 0) ──────────────── (L, 0)
  外向き方向：opt1 = 180°、opt2 = 0°
//}

導波路の中心線は @<tt>{[(0, 0), (length, 0)]} で定義されます。幅は中心線に対して対称に与えられます。

=== 初期値での形状

 * 中心線長：@<b>{100.0 µm}
 * 導波路幅：@<b>{0.5 µm}
 * 始点：@<b>{(0, 0) µm}
 * 終点：@<b>{(100, 0) µm}

図の端部形状は @<tt>{pya.Path} の表現・変換に依存します。ここでの「長さ」は@<b>{中心線長}を指します。

== パラメータ

//table[04-straight-t1][パラメータ・仕様一覧]{
パラメータ	型	初期値	単位	説明
------------------------------------------------------------
@<tt>{length}	@<tt>{TypeDouble}	100.0	µm	導波路中心線長
@<tt>{width}	@<tt>{TypeDouble}	0.5	µm	導波路幅
@<tt>{layer}	@<tt>{TypeLayer}	1/0	—	導波路を描画するレイヤー
@<tt>{pin_layer}	@<tt>{TypeLayer}	2/0	—	ポートを描画するレイヤー
//}

@<tt>{layer} と @<tt>{pin_layer} は @<tt>{Base.layers()} から継承します。v4のコードには @<tt>{length > 0} や @<tt>{width > 0} の明示的な入力検証がないため、運用時には正の値を指定してください。

== Python実装

v4の @<tt>{Straight} クラスを読みやすく整形すると次のようになります。

//emlist[python]{
class Straight(Base):
    def __init__(self):
        super(Straight, self).__init__()
        self.param("length", self.TypeDouble, "Length (um)", default=100.0)
        self.param("width", self.TypeDouble, "Width (um)", default=0.5)
        self.layers()

    def produce_impl(self):
        l, c = self.layout, self.cell
        wg = l.layer(self.layer)
        pin = l.layer(self.pin_layer)

        c.shapes(wg).insert(
            path_um([(0, 0), (self.length, 0)], self.width, l.dbu)
        )

        add_pin(c, l, pin, "opt1", 0, 0, 0, self.width)
        add_pin(c, l, pin, "opt2", self.length, 0, 180, self.width)
//}

=== 処理の流れ

 1. @<tt>{self.layout} と @<tt>{self.cell} からレイアウトとPCell生成先セルを取得します。
 1. @<tt>{l.layer(...)} で導波路レイヤーとPinレイヤーの内部インデックスを取得します。
 1. @<tt>{path_um(...)} でµm単位の中心線と幅から @<tt>{pya.Path} を生成します。
 1. @<tt>{c.shapes(wg).insert(...)} で導波路を描画します。
 1. @<tt>{add_pin(...)} を2回呼び出して、両端に名前付き光ポートを配置します。

== DBUと整数座標

共通関数は以下のとおりです。

//emlist[python]{
def q(v, dbu):
    return int(round(v / dbu))

def path_um(points, width, dbu):
    return pya.Path(
        [pya.Point(q(x, dbu), q(y, dbu)) for x, y in points],
        q(width, dbu)
    )
//}

@<tt>{q()} はµm単位の数値をDBU整数座標へ変換します。例えば @<b>{DBU = 0.001 µm} の場合、

//texequation{
100.0\,\mu\mathrm{m} \longrightarrow 100000\ \mathrm{DBU}
//}

//texequation{
0.5\,\mu\mathrm{m} \longrightarrow 500\ \mathrm{DBU}
//}

となります。DBUはレイアウトごとに異なるため、@<tt>{100000} や @<tt>{500} をコードに固定しないことが重要です。寸法はDBUに丸められるため、設定値と実際のGDS寸法には最大で概ね半DBU程度の量子化誤差が生じ得ます。

== Optical Portの定義

共通関数 @<tt>{add_pin()} は、Pinレイヤーに短いPathとポート名Textを挿入します。引数 @<tt>{inward_angle} は、@<b>{ポートからPCell内部へ向かう角度}です。

//table[04-straight-t2][パラメータ・仕様一覧]{
ポート	中心位置（µm）	内向き角度	外向き角度	幅
------------------------------------------------------------
@<tt>{opt1}	@<tt>{(0, 0)}	0°	180°	@<tt>{width}
@<tt>{opt2}	@<tt>{(length, 0)}	180°	0°	@<tt>{width}
//}

外向き角度への変換は次のとおりです。

//texequation{
\theta_{\mathrm{out}}=(\theta_{\mathrm{in}}+180^\circ)\bmod 360^\circ
//}

@<b>{注意：} v4の光ポートは専用のPythonポートオブジェクトではなく、レイアウト上の @<tt>{Path} と @<tt>{Text} です。外部ツールで認識する際は、名前・座標・方向の抽出規則を統一する必要があります。

== 導波路長と光学位相

Straightの中心線長は、そのままPCellの @<tt>{length} です。

//texequation{
\boxed{L_{\mathrm{WG}}=L}
//}

一様な単一モード導波路を仮定すると、伝搬位相は

//texequation{
\boxed{\phi=\beta L=\frac{2\pi n_{\mathrm{eff}}}{\lambda}L}
//}

で表されます。ここで @<tt>{n_eff} はモードの実効屈折率、@<tt>{λ} は真空波長です。@<b>{v4のPCellは @<tt>{n_eff} を計算しません。} 位相や損失を求めるには、対象プロセスのモード解析・測定データが必要です。

== KLayoutでの操作例

 1. KLayoutを起動し、v4マクロが読み込まれていることを確認します。
 1. PCellライブラリ @<b>{@<tt>{Photonics}} から @<b>{@<tt>{Straight}} を選択します。
 1. @<tt>{length = 100.0}、@<tt>{width = 0.5} を指定します。
 1. セル内に配置し、導波路レイヤー @<b>{1/0} とPinレイヤー @<b>{2/0} を表示します。
 1. 両端の @<tt>{opt1}・@<tt>{opt2} の位置と向きを確認します。
 1. @<tt>{length} を変更し、PCell形状と右端ポート位置が連動して変わることを確認します。

実際のメニュー名や配置手順はKLayoutのバージョン・UI設定により異なる場合があります。

== 設計・検証上の注意

//table[04-straight-t3][パラメータ・仕様一覧]{
項目	確認内容
------------------------------------------------------------
正の寸法	@<tt>{length > 0}、@<tt>{width > 0}
最小線幅	使用する製造プロセスのDRCに適合するか
DBU精度	@<tt>{width} がDBUに対して十分大きいか
接続幅	接続先ポートの導波路幅と一致するか
ポート方向	内向き・外向き角度を混同していないか
インスタンス変換	回転・反転・平行移動後のポート位置を正しく計算できるか
光学性能	損失・位相はレイアウト生成とは別途評価する
//}

== Photonics Router v6.xとの連携

@<tt>{Straight} は、Routerのポート検出・接続判定の基本テストに適しています。例えば、2つのStraightインスタンスを離して配置し、@<tt>{Straight_A.opt2} と @<tt>{Straight_B.opt1} を接続します。

//emlist[text]{
Straight_A                     Straight_B
opt1 ●════════● opt2     opt1 ●════════● opt2
                └── Router ───┘
//}

Router側では、各ポートの@<b>{インスタンス変換後の位置・方向・幅}を読み取る必要があります。ネットリストの概念的な表現例は次のとおりです（v4の出力形式ではありません）。

//emlist[text]{
Component: Straight_A
  type: Straight
  length_um: 100.0
  width_um: 0.5
  ports: [opt1, opt2]

Connection:
  from: Straight_A.opt2
  to:   Straight_B.opt1
//}

== v5への改善候補

 * @<tt>{length}、@<tt>{width} の妥当性検証と警告表示
 * ポートの外向き方向を共通メタデータとして明示
 * 中心線長・位相長のモデル連携
 * テーパー等の幅変化デバイスとの接続規則の整備
 * Routerによるポート抽出・接続テストの自動化

これらは@<b>{v4に実装済みの機能ではなく、今後の提案}です。

== まとめ

@<tt>{Straight} は最も基本的な2ポートPCellです。中心線は @<tt>{(0,0)} から @<tt>{(length,0)} までの直線で、初期値は@<b>{長さ100 µm、幅0.5 µm}です。両端の光ポートはPinレイヤー上のPathとTextで表現されます。

Straightを基準として、座標変換、光ポート抽出、DBU処理を検証することで、ほかのPCellやPhotonics Routerとの接続処理を安定させられます。



@<b>{次章：} [第5章 Bend90 — 90°円弧導波路](05_bend90.md)（制作予定）


=== PCell構造図（v4初期パラメータ）

//image[04-straight-1][04_straight の中心線・MMI領域・Optical Port][scale=0.8]{
//}

@<i>{青：導波路中心線、淡青：MMI領域、橙矢印：@<tt>{add_pin()} の内向き方向。図はPython実装の座標式に基づく概念図であり、KLayoutのGDSレンダリングではありません。}
