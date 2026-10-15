= Ring — リング共振器

@<b>{対象実装:} @<tt>{pymacros/photonics_pdk_v4.lym} の @<tt>{class Ring(Base)}  
@<b>{確認日:} 2026-10-15  
@<b>{対象:} KLayout Silicon Photonics PDK v4

== 概要

@<tt>{Ring} は、直線状のバス導波路と円環状の導波路を隣接配置する、@<b>{単一バス型（all-pass型）リング共振器}のレイアウトPCellである。バス導波路の入力から光を入射し、リングの共振条件に応じた透過特性を得ることを想定している。v4は形状生成用であり、透過スペクトル、結合係数、損失などを自動計算しない。

== 構造と座標系

//emlist[text]{
                     y ↑
                       │       リング中心 (cx, cy)
                       │           ○
                       │       .-''''''-.
                       │      /          \
                       │      \          /
                       │       '-.____.-'
                       │           ↑
                       │       edge gap = gap
                       │
     opt1 (0,0)  ●══════╪══════════════════● opt2 (bus_length,0)
                       └────────────────────────→ x
                       バス導波路中心線 y=0
//}

リングの中心と半径は、ソースコード上で次のように定義される。

//texequation{
c_x=\frac{\mathrm{bus\_length}}{2},\qquad
c_y=\mathrm{radius}+\mathrm{gap}+\mathrm{width}.
//}

したがってリング中心線の最下点は \(y=\mathrm{gap}+\mathrm{width}\) に位置する。バス導波路とリング導波路の中心線間隔は \(\mathrm{gap}+\mathrm{width}\)、両導波路の@<b>{外縁間の最短距離}は、両者が同じ幅である場合、指定した @<tt>{gap} になる。

== PCellパラメータ

//table[08-ring-t1][パラメータ・仕様一覧]{
パラメータ	型	v4初期値	内容
------------------------------------------------------------
@<tt>{radius}	@<tt>{TypeDouble}	10.0 µm	リング中心線の半径
@<tt>{width}	@<tt>{TypeDouble}	0.5 µm	バス・リング共通の導波路幅
@<tt>{gap}	@<tt>{TypeDouble}	0.2 µm	バスとリングの導波路外縁間のギャップ
@<tt>{bus_length}	@<tt>{TypeDouble}	40.0 µm	バス導波路の長さ
@<tt>{points}	@<tt>{TypeInt}	128	リングを近似する線分数（実装下限48）
@<tt>{layer}	@<tt>{TypeLayer}	(1, 0)	導波路レイヤー
@<tt>{pin_layer}	@<tt>{TypeLayer}	(2, 0)	Optical Portレイヤー
//}

上記の初期値は公開v4の@<tt>{Ring.__init__()}に基づく。物理的に成立する値域の検証は、実装に明示されていない。

== Python実装の構造

公開v4の処理を要約すると、次のとおりである。

//emlist[python]{
# 1. バス導波路を生成
c.shapes(wg).insert(
    path_um([(0, 0), (self.bus_length, 0)], self.width, l.dbu)
)

# 2. リング中心を決定
cx = self.bus_length / 2
cy = self.radius + self.gap + self.width
n = max(48, int(self.points))

# 3. 円周を離散点列に変換
pts = [
    (
        cx + self.radius * math.cos(2 * math.pi * i / n),
        cy + self.radius * math.sin(2 * math.pi * i / n)
    )
    for i in range(n + 1)
]
c.shapes(wg).insert(path_um(pts, self.width, l.dbu))

# 4. バス導波路両端に光ポートを配置
add_pin(c, l, pin, "opt1", 0, 0, 0, self.width)
add_pin(c, l, pin, "opt2", self.bus_length, 0, 180, self.width)
//}

上記は@<tt>{produce_impl()}の主要処理を抜粋・整形したものである。リングは @<tt>{i=0} から @<tt>{n} までの @<tt>{n+1} 点で定義され、最後の点が最初の点と一致する閉曲線を @<tt>{pya.Path} として描画する。@<b>{ポリゴンによる円環の差分生成ではない}点に注意する。

== リング長と共振条件

理想的な円形中心線の一周長は

//texequation{
\boxed{L_\mathrm{ring}=2\pi R}
//}

である。初期値 \(R=10\,\mu\mathrm{m}\) では \(L_\mathrm{ring}\approx62.832\,\mu\mathrm{m}\) となる。

リング内の伝搬位相が整数倍の \(2\pi\) になると共振が起こる。

//texequation{
\beta(\lambda_m)L_\mathrm{ring}=2\pi m,
\qquad \beta=\frac{2\pi n_\mathrm{eff}(\lambda)}{\lambda}.
//}

したがって

//texequation{
\boxed{m\lambda_m=n_\mathrm{eff}(\lambda_m)L_\mathrm{ring}}
//}

である。ただし、実際の共振波長を求めるには、導波路断面と材料に依存する有効屈折率 \(n_\mathrm{eff}\) が必要である。@<b>{半径だけでは共振波長を確定できない}。

== FSR（自由スペクトル間隔）

隣接する共振波長間隔は、波長領域で近似的に

//texequation{
\boxed{\mathrm{FSR}_{\lambda}\approx\frac{\lambda^2}{n_gL_\mathrm{ring}}}
//}

と表される。\(n_g\) は群屈折率である。たとえば、@<b>{説明用の仮定}として \(\lambda=1.55\,\mu\mathrm{m}\)、\(n_g=4.0\)、\(R=10\,\mu\mathrm{m}\) とすると、

//texequation{
\mathrm{FSR}_{\lambda}\approx
\frac{1.55^2}{4.0\times2\pi\times10}\,\mu\mathrm{m}
\approx0.00956\,\mu\mathrm{m}=9.56\,\mathrm{nm}.
//}

この値は@<b>{シミュレーションや測定による検証値ではない}。

== ギャップと結合

@<tt>{gap} はバス導波路とリング導波路のエバネッセント結合に影響する重要なパラメータである。一般に、他の条件が等しければギャップが小さいほど結合が強くなる傾向があるが、結合係数は幅、層厚、屈折率、波長、偏波、曲率などにも依存する。

v4では @<tt>{gap} を変更すると@<b>{レイアウト上の位置関係のみ}が更新され、結合係数や臨界結合条件は計算されない。結合設計にはモード解析や電磁界シミュレーションが必要である。

== 円周の離散化と誤差

@<tt>{points = N} としたとき、リング中心線は \(N\) 本の弦で近似される。理想円と各弦の最大偏差（サジッタ）は

//texequation{
\boxed{\delta=R\left(1-\cos\frac{\pi}{N}\right)}
//}

である。初期値 \(R=10\,\mu\mathrm{m}\)、\(N=128\) では \(\delta\approx0.00301\,\mu\mathrm{m}=3.01\,\mathrm{nm}\)。実際の座標はさらにDBUで丸められるため、最終的な形状誤差はDBUにも依存する。

離散化された中心線長は

//texequation{
L_N=2NR\sin\left(\frac{\pi}{N}\right)
//}

であり、理想円周長 \(2\pi R\) よりわずかに短い。

== Optical Portの定義

//table[08-ring-t2][パラメータ・仕様一覧]{
ポート	座標 (µm)	@<tt>{add_pin}の内向き角度	接続対象
------------------------------------------------------------
@<tt>{opt1}	@<tt>{(0, 0)}	0°	バス左端
@<tt>{opt2}	@<tt>{(bus_length, 0)}	180°	バス右端
//}

リング自体には独立した光ポートが定義されていない。v4の@<tt>{add_pin}はPinレイヤーに短いPathと名前のTextを配置する。@<b>{角度は素子内部を向く方向}として扱う。

== KLayoutでの確認手順

 1. PDK v4マクロをKLayoutに読み込み、PCellライブラリ @<tt>{Photonics} の @<tt>{Ring} を配置する。
 1. @<tt>{radius=10}, @<tt>{width=0.5}, @<tt>{gap=0.2}, @<tt>{bus_length=40}, @<tt>{points=128} を確認する。
 1. Waveguideレイヤー @<tt>{(1,0)} とPinレイヤー @<tt>{(2,0)} を表示する。
 1. バス両端の @<tt>{opt1} / @<tt>{opt2} を確認する。
 1. @<tt>{gap} を変更してリング位置が変化すること、@<tt>{points} を変更して多角形近似が変わることを確認する。
 1. 意図しない重なりや製造ルール違反がないか、別途DRCで確認する。

== Photonics Router v6.xとの連携

Ringの外部接続対象はバス導波路の2ポートである。Router側で接続判定を行う場合、インスタンスの配置変換を考慮し、ポート位置と向きをグローバル座標へ変換する必要がある。

@<b>{重要:} v4のPinレイヤー上のPath/Textは、Routerが自動的に認識することを保証しない。ポート抽出方式と命名規則が一致するか、Router側で検証する必要がある。また、リングとバスの間は幾何学的に非接触でも光学的に結合するため、単純な接触判定によるネットリストでは結合を表現できない。

== v5への改善提案

 * @<tt>{radius > 0}、@<tt>{width > 0}、@<tt>{gap >= 0} などの入力検証を追加する。
 * リング導波路幅とバス導波路幅を独立パラメータにする。
 * 円周近似の最大許容誤差から@<tt>{points}を自動決定できるようにする。
 * リング共振器の結合関係をネットリスト上で表現する仕組みを追加する。
 * @<tt>{n_eff}、@<tt>{n_g}、損失、結合係数を外部モデルと関連付ける。ただし、レイアウトPCellと光学モデルの責務を明確に分離する。
 * add-drop型を別PCellとして追加する。

これらは@<b>{今後の改善案}であり、v4に実装されている機能ではない。

== まとめ

@<tt>{Ring} はバス導波路と円形リングを生成する単一バス型共振器PCellである。主要な設計値はリング中心線半径 @<tt>{radius}、導波路幅 @<tt>{width}、外縁間隔 @<tt>{gap}、バス長 @<tt>{bus_length} である。v4は形状と2つの光ポートを生成するが、共振波長・FSR・結合係数を確定するには別途光学モデルが必要となる。



@<b>{参照実装:} photonics_pdk_v4.lym (https://github.com/TAKE-HooJoo/klayout-photonics-pdk/blob/main/pymacros/photonics_pdk_v4.lym)（@<tt>{Ring} クラス）


=== PCell構造図（v4初期パラメータ）

//image[08-ring-1][08_ring の中心線・MMI領域・Optical Port][scale=0.8]{
//}

@<i>{青：導波路中心線、淡青：MMI領域、橙矢印：@<tt>{add_pin()} の内向き方向。図はPython実装の座標式に基づく概念図であり、KLayoutのGDSレンダリングではありません。}
