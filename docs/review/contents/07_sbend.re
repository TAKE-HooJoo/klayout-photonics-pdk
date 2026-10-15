= SBend — S字導波路

@<b>{対象:} @<tt>{pymacros/photonics_pdk_v4.lym} の @<tt>{class SBend(Base)}  
@<b>{確認日:} 2026-10-15  
@<b>{位置づけ:} PCell Library v4の実装仕様と、光学設計上の留意点を区別して解説する。

== 概要

@<tt>{SBend} は、入口と出口の@<b>{接線方向を水平に保ったまま}、導波路の中心線を垂直方向へ @<tt>{offset} だけ移動させるPCellである。隣接する光学部品のポート高さが異なる場合の接続や、導波路間隔の調整に使用できる。

v4のSBendは@<b>{3次Bézier曲線}で構成される。Euler曲線や一定曲率の円弧とは異なる。

== 構造と座標

//emlist[text]{
      y
      ↑                        opt2 (L, H)
      │                    ____● → 右向きの導波路接線
      │                ___/
      │            ___/
      │       ____/
      │  ____/
      ●────────────────────────────→ x
   opt1 (0,0)

   L = length, H = offset
   両端の導波路接線は水平
//}

上図は概念図であり、曲線の正確な形状は後述のBézier式で定義される。@<tt>{offset < 0} なら下方向に移動する。

== パラメータ

//table[07-sbend-t1][パラメータ・仕様一覧]{
パラメータ	型	v4初期値	意味
------------------------------------------------------------
@<tt>{length}	@<tt>{TypeDouble}	@<tt>{20.0} µm	始点から終点までのX方向距離 @<tt>{L}
@<tt>{offset}	@<tt>{TypeDouble}	@<tt>{5.0} µm	終点のY方向変位 @<tt>{H}
@<tt>{width}	@<tt>{TypeDouble}	@<tt>{0.5} µm	導波路幅
@<tt>{points}	@<tt>{TypeInt}	@<tt>{64}	Bézier曲線の分割数（下限16）
@<tt>{layer}	@<tt>{TypeLayer}	@<tt>{(1, 0)}	導波路レイヤー（共通Base）
@<tt>{pin_layer}	@<tt>{TypeLayer}	@<tt>{(2, 0)}	光ポートレイヤー（共通Base）
//}

@<tt>{length} は@<b>{中心線の実際の弧長ではない}。弧長は曲線形状に応じて長くなる。

== 3次Bézier曲線

制御点は、v4のソースコードに従って次のように設定される。

//texequation{
P_0=(0,0),\quad P_1=(0.35L,0),\quad
P_2=(0.65L,H),\quad P_3=(L,H)
//}

曲線は、パラメータ \(t\in[0,1]\) に対して

//texequation{
\boxed{B(t)=(1-t)^3P_0+3(1-t)^2tP_1+3(1-t)t^2P_2+t^3P_3}
//}

で表される。座標を展開すると

//texequation{
x(t)=L\{1.05(1-t)^2t+1.95(1-t)t^2+t^3\},
\qquad y(t)=H(3t^2-2t^3).
//}

=== 両端の接線

Bézier曲線の導関数は

//texequation{
B'(0)=3(P_1-P_0)=(1.05L,0),\quad
B'(1)=3(P_3-P_2)=(1.05L,0).
//}

したがって @<b>{@<tt>{length > 0} なら始点と終点の接線はともに +X方向}である。これは水平導波路との滑らかな接続に有利である。一方、@<tt>{length = 0} では端点の導関数がゼロになり、接線の定義が不安定になるため避ける。

== v4のPython実装

以下は公開ソースの @<tt>{SBend} に対応する主要処理である（読みやすさのため改行・コメントを整理）。

//emlist[python]{
class SBend(Base):
    def __init__(self):
        super(SBend, self).__init__()
        self.param("length", self.TypeDouble, "Length (um)", default=20.0)
        self.param("offset", self.TypeDouble, "Vertical offset (um)", default=5.0)
        self.param("width", self.TypeDouble, "Width (um)", default=0.5)
        self.param("points", self.TypeInt, "Points", default=64)
        self.layers()

    def produce_impl(self):
        l, c = self.layout, self.cell
        L, y = self.length, self.offset
        pts = bezier(
            (0, 0), (L * 0.35, 0),
            (L * 0.65, y), (L, y),
            max(16, int(self.points))
        )
        c.shapes(l.layer(self.layer)).insert(
            path_um(pts, self.width, l.dbu)
        )
        pin = l.layer(self.pin_layer)
        add_pin(c, l, pin, "opt1", 0, 0, 0, self.width)
        add_pin(c, l, pin, "opt2", L, y, 180, self.width)
//}

共通関数 @<tt>{bezier()} は @<tt>{t=i/n}（@<tt>{i=0,...,n}）の @<b>{@<tt>{n+1} 個のサンプル点}を返す。@<tt>{path_um()} は座標と幅をDBUへ変換し、@<tt>{pya.Path}を生成する。

== Optical Port

//table[07-sbend-t2][パラメータ・仕様一覧]{
ポート	座標（µm）	@<tt>{add_pin} に渡す角度	意味
------------------------------------------------------------
@<tt>{opt1}	@<tt>{(0, 0)}	@<tt>{0°}	左端からPCell内部へ向かう方向は +X
@<tt>{opt2}	@<tt>{(length, offset)}	@<tt>{180°}	右端からPCell内部へ向かう方向は −X
//}

@<b>{注意:} @<tt>{add_pin()} の引数は @<tt>{inward_angle}（PCell内部を向く角度）である。出口の導波路接線が +X でも、@<tt>{opt2} の@<b>{内向き}角度は180°になる。外向き方向を扱うRouterでは角度を反転して解釈する必要がある。

== 導波路長

実際の中心線長は

//texequation{
\boxed{S=\int_0^1\sqrt{\left(\frac{dx}{dt}\right)^2+\left(\frac{dy}{dt}\right)^2}\,dt}
//}

で求める。v4のPCellはこの積分値をプロパティとして出力しない。数値積分、または離散化された中心線の点間距離の総和で評価する。

@<tt>{length=20 µm}, @<tt>{offset=5 µm} の初期設定では、Sは20 µmより長い。正確な値は数値積分・量子化条件で変化する。

== 曲率と光学設計

平面曲線の曲率は

//texequation{
\kappa(t)=\frac{|x'(t)y''(t)-y'(t)x''(t)|}
{\left(x'(t)^2+y'(t)^2\right)^{3/2}},
\qquad R(t)=\frac{1}{\kappa(t)}.
//}

端点の接線が水平であっても、@<b>{端点の曲率がゼロとは限らない}。このv4実装では @<tt>{offset ≠ 0} の場合、端点の曲率は一般に非ゼロであり、直線導波路との接続点で曲率が不連続となる。低損失設計を目指す場合は、最小曲率半径、曲率連続性、導波モードへの影響を別途評価する。

@<tt>{length} を短くして @<tt>{offset} を大きくすると、一般に曲げが急になる。レイアウト形状が生成できても、光学的な許容損失を満たすとは限らない。

== 離散化・DBU・入力値の注意

 * @<tt>{points} の実効値は @<tt>{max(16, int(points))} である。
 * 曲線は折れ線として @<tt>{pya.Path} に渡される。サンプル数とDBUは形状精度に影響する。
 * v4には @<tt>{length > 0}、@<tt>{width > 0}、最小曲率半径などの入力検証がない。
 * @<tt>{offset = 0} の場合、幾何学的には水平な直線となる。
 * @<tt>{length < 0} では接線方向や光ポートの向きがv4の固定角度と整合しなくなる可能性があるため、通常の設計では避ける。

== KLayoutでの確認手順

 1. @<tt>{photonics_pdk_v4.lym} をKLayoutのPythonマクロとして読み込む。
 1. PCellライブラリー @<tt>{Photonics} から @<tt>{SBend} を選択する。
 1. @<tt>{length=20}, @<tt>{offset=5}, @<tt>{width=0.5}, @<tt>{points=64} を設定する。
 1. Waveguideレイヤー @<tt>{(1,0)} とPinレイヤー @<tt>{(2,0)} を表示する。
 1. 始点 @<tt>{(0,0)}、終点 @<tt>{(20,5)}、@<tt>{opt1} と @<tt>{opt2} の位置・向きを確認する。
 1. @<tt>{offset} を負に変更し、上下方向の反転を確認する。

== Photonics Router v6.xとの連携

SBendは、水平接線を持つ2ポートの導波路部品としてRouterの接続候補になる。ただし、v4のポートはPinレイヤー上の @<tt>{Path} と @<tt>{Text} で表現され、@<b>{構造化されたポートメタデータがPCellから直接返されるわけではない}。Router側で名前、位置、内向き方向、幅、階層変換を正しく解釈する必要がある。

Router v6.xの個別バージョンでの自動認識・ネットリスト生成の挙動は、この章だけでは検証済みとはしない。

== PCell Library v5への改善案（未実装）

 1. @<tt>{length > 0}、@<tt>{width > 0}、@<tt>{points} の入力検証を追加する。
 1. 最小曲率半径を算出し、設計ルール違反を検出する。
 1. 中心線長を計算し、光路長評価に利用できるようにする。
 1. 必要に応じて端点曲率ゼロの曲線方式を選択できるようにする。
 1. 光ポートの位置・方向・幅を共通仕様で出力する。
 1. 設計波長・導波路断面に基づく光学シミュレーションと照合する。

== まとめ

@<tt>{SBend} は、3次Bézier曲線を用いて水平接線を保ちながら導波路を上下に移動するPCellである。v4の初期値は @<b>{@<tt>{length=20 µm}、@<tt>{offset=5 µm}、@<tt>{width=0.5 µm}、@<tt>{points=64}}。光ポートは @<tt>{opt1=(0,0)}、@<tt>{opt2=(length,offset)} に置かれる。接線連続性と曲率連続性は異なるため、光学設計では最小曲率半径と接続損失の確認が重要となる。



@<b>{参照実装:} @<tt>{photonics_pdk_v4.lym} (https://github.com/TAKE-HooJoo/klayout-photonics-pdk/blob/main/pymacros/photonics_pdk_v4.lym) の @<tt>{bezier()}、@<tt>{add_pin()}、@<tt>{SBend}。


=== PCell構造図（v4初期パラメータ）

//image[07-sbend-1][07_sbend の中心線・MMI領域・Optical Port][scale=0.8]{
//}

@<i>{青：導波路中心線、淡青：MMI領域、橙矢印：@<tt>{add_pin()} の内向き方向。図はPython実装の座標式に基づく概念図であり、KLayoutのGDSレンダリングではありません。}
