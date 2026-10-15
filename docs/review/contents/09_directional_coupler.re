= DirectionalCoupler — 方向性結合器

@<b>{対象実装:} @<tt>{pymacros/photonics_pdk_v4.lym} の @<tt>{class DirectionalCoupler(Base)}  
@<b>{確認日:} 2026-10-15  
@<b>{対象:} KLayout Silicon Photonics PDK v4

== 概要

@<tt>{DirectionalCoupler} は、近接して並走する2本の光導波路間のエバネッセント結合を利用する、@<b>{4ポートの方向性結合器}のレイアウトPCellである。中央の直線結合領域と、その両側のS字アクセス導波路から構成される。分岐器、光スイッチ、干渉計などの構成要素として利用できる。

@<b>{重要:} v4が生成するのは幾何形状と光ポートであり、所望の50:50分岐比や結合効率を保証するものではない。結合係数は導波路断面、材料、波長、偏波、ギャップ等に依存する。

== 構造と座標系

//emlist[text]{
                  y ↑
 opt1 ●──────╲__________________╱──────● opt3  (y=+p)
                 ────────────────        結合領域 y=+s
                 ────────────────        結合領域 y=-s
 opt2 ●──────╱‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾╲──────● opt4  (y=-p)
      x=0        x=a         x=a+L      x=2a+L  → x

  a = access_length       L = coupling_length
  p = port_spacing/2      s = (gap+width)/2
//}

上図は@<b>{概念図}であり、実際の曲線は3次Bézier曲線である。上下の導波路はx軸に関して対称で、左端の2ポートから中央の結合領域へ近づき、右端で再び離れる。

中央部の導波路中心線間隔は

//texequation{
  d_{\mathrm{center}}=2s=\mathrm{gap}+\mathrm{width}.
//}

両導波路の幅が @<tt>{width} であるため、中央直線部の@<b>{エッジ間ギャップ}は @<tt>{gap} となる（@<tt>{gap ≥ 0} かつ正の幅を想定）。

== PCellパラメータ

//table[09-directional-coupler-t1][パラメータ・仕様一覧]{
パラメータ	型	v4初期値	内容
------------------------------------------------------------
@<tt>{coupling_length}	@<tt>{TypeDouble}	20.0 µm	中央直線結合部の長さ
@<tt>{access_length}	@<tt>{TypeDouble}	15.0 µm	片側S字アクセス部のx方向長さ
@<tt>{gap}	@<tt>{TypeDouble}	0.2 µm	中央直線部の導波路エッジ間隔
@<tt>{port_spacing}	@<tt>{TypeDouble}	5.0 µm	左右端の上下ポート中心間隔
@<tt>{width}	@<tt>{TypeDouble}	0.5 µm	両導波路共通の幅
@<tt>{layer}	@<tt>{TypeLayer}	(1, 0)	導波路レイヤー（共通@<tt>{Base}由来）
@<tt>{pin_layer}	@<tt>{TypeLayer}	(2, 0)	光ポートレイヤー（共通@<tt>{Base}由来）
//}

v4ではアクセス部のBézier曲線は@<b>{各48分割に固定}されており、曲線分割数をPCellパラメータから変更する仕組みはない。

初期値の場合、@<tt>{a=15}, @<tt>{L=20}, @<tt>{p=2.5}, @<tt>{s=0.35}（すべてµm）で、全体のx方向長さは

//texequation{
 X=2a+L=50\ \mathrm{µm}.
//}

== Pythonソースコードの解説

以下は公開v4の @<tt>{produce_impl()} にある主要処理を、読みやすく改行したものである。

//emlist[python]{
l, c = self.layout, self.cell
wg = l.layer(self.layer)
pin = l.layer(self.pin_layer)

a = self.access_length
L = self.coupling_length
s = (self.gap + self.width) / 2
p = self.port_spacing / 2

top = (
    bezier((0, p), (a * .35, p), (a * .65, s), (a, s), 48)
    + [(a + L, s)]
    + bezier(
        (a + L, s),
        (a + L + a * .35, s),
        (a + L + a * .65, p),
        (2 * a + L, p),
        48
    )[1:]
)
bot = [(x, -y) for x, y in top]

c.shapes(wg).insert(path_um(top, self.width, l.dbu))
c.shapes(wg).insert(path_um(bot, self.width, l.dbu))

x = 2 * a + L
add_pin(c, l, pin, "opt1", 0, p, 0, self.width)
add_pin(c, l, pin, "opt2", 0, -p, 0, self.width)
add_pin(c, l, pin, "opt3", x, p, 180, self.width)
add_pin(c, l, pin, "opt4", x, -p, 180, self.width)
//}

処理は次の4段階に整理できる。

 1. @<tt>{s} と @<tt>{p} を計算し、結合部と外部ポートの上下位置を決める。
 1. 上側導波路 @<tt>{top} を、入力側Bézier曲線・中央直線・出力側Bézier曲線の点列として構築する。
 1. @<tt>{bot=[(x,-y) for x,y in top]} によって下側導波路をx軸対称に生成する。
 1. 2本の導波路を描画し、4つの名前付き光ポートを生成する。

@<tt>{bezier(...)[1:]} は、出力側曲線の最初の点が中央直線部の終点と重複するのを避ける処理である。入力側Bézier曲線は49点、中央直線の終点が1点、出力側曲線の追加分が48点なので、上側中心線の点列は@<b>{合計98点}となる。

== 3次Bézierアクセス導波路

入力側の上側導波路は、次の4制御点を用いる。

//texequation{
P_0=(0,p),\quad P_1=(0.35a,p),\quad
P_2=(0.65a,s),\quad P_3=(a,s).
//}

3次Bézier曲線は

//texequation{
B(t)=(1-t)^3P_0+3(1-t)^2tP_1+3(1-t)t^2P_2+t^3P_3,\qquad 0\le t\le1.
//}

端点での接線は

//texequation{
B'(0)=3(P_1-P_0)=(1.05a,0),
//}

//texequation{
B'(1)=3(P_3-P_2)=(1.05a,0).
//}

したがって @<tt>{a>0} なら、アクセス曲線の両端は水平方向を向く。中央直線部と接続する箇所でも@<b>{接線方向が連続}する。一方、@<b>{曲率まで連続するとは限らない}。低損失設計の観点では、接続点の曲率変化と最小曲率半径の検証が別途必要である。

== Optical Portの定義

//table[09-directional-coupler-t2][パラメータ・仕様一覧]{
ポート	座標 (µm)	@<tt>{inward_angle}	接続方向の解釈
------------------------------------------------------------
@<tt>{opt1}	@<tt>{(0, +p)}	0°	左上、セル内向きは +x
@<tt>{opt2}	@<tt>{(0, -p)}	0°	左下、セル内向きは +x
@<tt>{opt3}	@<tt>{(2a+L, +p)}	180°	右上、セル内向きは −x
@<tt>{opt4}	@<tt>{(2a+L, -p)}	180°	右下、セル内向きは −x
//}

初期値では以下となる。

//emlist[text]{
opt1 = ( 0, +2.5) µm  inward=0°
opt2 = ( 0, -2.5) µm  inward=0°
opt3 = (50, +2.5) µm  inward=180°
opt4 = (50, -2.5) µm  inward=180°
//}

共通関数 @<tt>{add_pin()} は、Pinレイヤーに短い @<tt>{pya.Path} と @<tt>{pya.Text} を配置する。角度は@<b>{外向き法線ではなく、ポートからセル内部へ向かう方向}である点に注意する。v4のポートはテキストと形状であり、明示的なモード番号・偏波・光学ネットリスト情報は保持していない。

== 光結合の理論

同一の単一モード導波路2本からなる理想的な、損失のない対称方向性結合器を仮定する。中央の平行結合区間において、結合係数を @<tt>{κ} [1/µm]、長さを @<tt>{L} とすると、単一ポートから入射した光の概略的なパワー比は

//texequation{
P_{\mathrm{through}}=\cos^2(\kappa L),\qquad
P_{\mathrm{cross}}=\sin^2(\kappa L).
//}

理想的な50:50分岐の条件の一つは

//texequation{
\kappa L=\frac{\pi}{4}\quad(\mathrm{mod}\ \pi/2)
//}

である。@<b>{ただし、これはアクセス領域での結合を無視した簡略モデル}であり、実際にはアクセス部でも導波路が近づくため結合が発生し得る。結合領域全体を含むモード解析・EME・FDTD等による検証が必要となる。

導波路間の伝搬定数不整合 @<tt>{Δβ} がある場合には、完全結合を前提とした上式をそのまま適用できない。結合係数 @<tt>{κ} と @<tt>{Δβ} を用いる結合モード理論や、偶・奇スーパーモードの実効屈折率から結合長を評価する。

//texequation{
L_{\pi}=\frac{\pi}{\lvert\beta_{\mathrm{even}}-\beta_{\mathrm{odd}}\rvert}
//}

は、理想的な同一導波路のスーパーモード解析における、入射導波路から反対側へパワーが最大移行する長さの一例である（定義の取り方によって「結合長」の呼称が異なるため注意）。

== 導波路長と光学位相

各経路の中心線長は、入力アクセス部・中央直線部・出力アクセス部の合計である。

//texequation{
L_{\mathrm{path}}=L+2L_{\mathrm{access}},\qquad
L_{\mathrm{access}}=\int_0^1\lVert B'(t)\rVert\,dt.
//}

@<tt>{access_length} はアクセス部の@<b>{x方向長さ}であり、実際の曲線長ではない。上下経路は鏡映対称なので、理想的な幾何学的中心線長は等しい。ただし、曲線の離散化とDBU丸めによって微小な誤差が生じ得る。

== 離散化とDBU

@<tt>{bezier()} は @<tt>{n=48} に対して @<tt>{n+1=49} 点を返す。@<tt>{path_um()} は各座標を @<tt>{q(v,dbu)=int(round(v/dbu))} で整数DBU座標に変換し、@<tt>{pya.Path} を生成する。したがって、細かな形状の再現性はDBUとサンプリング点数に依存する。

設計値に対してギャップが小さい場合、@<b>{DBU丸めによる実効ギャップの変化}を確認すること。曲線が十分に細かく近似されているかは、描画表示だけでなく生成された形状の測定によって評価する。

== KLayoutでの確認手順

 1. @<tt>{photonics_pdk_v4.lym} をKLayoutのマクロとして読み込み、@<tt>{Photonics} ライブラリが登録されていることを確認する。
 1. @<tt>{DirectionalCoupler} PCellを配置し、初期値で2本の導波路が左右対称に接続されているか確認する。
 1. レイヤー @<tt>{(1,0)} に導波路、@<tt>{(2,0)} に @<tt>{opt1}〜@<tt>{opt4} のPinとラベルが生成されているか確認する。
 1. @<tt>{gap} を変更し、中央結合部のエッジ間隔が期待どおりに変わるか確認する。
 1. @<tt>{port_spacing} と @<tt>{access_length} を変更し、アクセス曲線の形状・曲率・重なりの有無を確認する。
 1. 必要に応じてDRC、導波路断面解析、結合効率の電磁界シミュレーションを実施する。

== Photonics Router v6.xとの連携

v4の @<tt>{DirectionalCoupler} は、4つのポート位置と向きをPinレイヤー上に明示するため、@<b>{ポート検出型Routerに接続するための基本情報}を備える。ただし、Routerが実際に認識できるかどうかは、Router側のレイヤー設定・Text解釈・階層変換・方向定義に依存する。

検証時には、次の事項を確認する。

 * 4ポートすべての名前・位置・角度が正しく抽出されること。
 * インスタンスの回転・鏡映後にも、ポート座標と方向が正しく変換されること。
 * @<tt>{opt1}〜@<tt>{opt4} の接続関係を、単なる交差や幾何学的接触と混同しないこと。
 * 方向性結合器をネットリスト上で@<b>{4端子の光学素子}として表現できること。

== v4の制約とv5への改善案

//table[09-directional-coupler-t3][パラメータ・仕様一覧]{
項目	v4の現状	改善案（未実装）
------------------------------------------------------------
分岐比	形状のみ、分岐比の保証なし	波長・偏波別の結合係数モデルを連携
曲線分割数	各アクセス部48固定	サンプリング数のパラメータ化
入力値検証	明示的な値域検証なし	正の幅・長さ、非負ギャップなどを検証
曲率	Bézier形状、曲率制約なし	最小曲率半径チェックと最適化
光ポート	Pin Path + Text	ポートメタデータの明示的管理
ネットリスト	PCell自体はモデルを持たない	4ポート素子モデルとの対応付け
レイアウト検証	自動光学検証なし	DRC・EME/FDTD結果との連携
//}

特に @<tt>{port_spacing} が中央の中心線間隔 @<tt>{gap+width} より小さい場合、アクセス部が「中央へ近づく」形状とは限らない。パラメータの組合せに応じて、曲線形状と最小ギャップを検査することが望ましい。

== まとめ

@<tt>{DirectionalCoupler} は、2本の鏡映対称な導波路、中央直線結合部、左右の3次Bézierアクセス部、および4つの光ポートから構成される。初期値では全長50 µm、中央エッジ間ギャップ0.2 µm、外部ポート間隔5 µmとなる。

@<b>{設計上の核心は、幾何学的な @<tt>{coupling_length} と @<tt>{gap} を設定するだけでは、目標分岐比は確定しない}という点である。実際の結合効率は導波路断面、モード、波長、アクセス部の影響を含めて評価する必要がある。



@<b>{実装参照:} @<tt>{pymacros/photonics_pdk_v4.lym} (https://github.com/TAKE-HooJoo/klayout-photonics-pdk/blob/main/pymacros/photonics_pdk_v4.lym) の @<tt>{DirectionalCoupler}、共通関数 @<tt>{bezier()}、@<tt>{path_um()}、@<tt>{add_pin()}。


=== PCell構造図（v4初期パラメータ）

//image[09-directional-coupler-1][09_directional_coupler の中心線・MMI領域・Optical Port][scale=0.8]{
//}

@<i>{青：導波路中心線、淡青：MMI領域、橙矢印：@<tt>{add_pin()} の内向き方向。図はPython実装の座標式に基づく概念図であり、KLayoutのGDSレンダリングではありません。}
