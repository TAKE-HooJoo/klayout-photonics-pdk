= EulerBend — Euler型曲げ導波路

@<b>{実装基準}：@<tt>{pymacros/photonics_pdk_v4.lym} (https://github.com/TAKE-HooJoo/klayout-photonics-pdk/blob/main/pymacros/photonics_pdk_v4.lym)。本章は既存の第3章に記録されたv4仕様と曲線理論を基にした@<b>{技術解説書の初稿}です。GitHubの現行ソースをこの作成時点で再取得できなかったため、コード例は@<b>{参考実装}であり、v4の逐語引用ではありません。特に曲線生成アルゴリズム、ポート角度、正規化処理は公開前にソース照合してください。

@<b>{ソース照合追記（2026-10-15）:} ユーザー提供のv4ソースを静的解析した。実装は @<tt>{n=max(32,int(points))} の中点法で、正規化パラメータ @<tt>{u} に対して @<tt>{k=4u}（前半）および @<tt>{k=4(1-u)}（後半）を使用する。接線角を @<tt>{th += (π/2)*k/n} で積算し、@<tt>{cos(th), sin(th)} で座標を逐次更新した後、終点が @<tt>{(radius,radius)} となるようX/Yを別々にスケーリングする。したがって@<b>{厳密なFresnel積分によるクロソイドではなく、数値積分・異方的スケーリングによるEuler型近似}である。光学損失や曲率連続性の保証はない。KLayout実行検証は未実施。

== 概要と用途

@<tt>{EulerBend}は、曲率が経路に沿って変化するEuler（Clothoid、クロソイド）型の曲げ導波路を生成するPCellです。直線と一定半径の円弧を直接接続すると、接続位置で曲率が0から@<tt>{1/R}へ不連続に変化します。Euler型曲線は曲率を徐々に増減させることで、この不連続を緩和する設計に使われます。

ただし、@<b>{Euler型という名称だけで低損失が保証されるわけではありません}。光学性能は導波路断面、偏光、波長、曲率分布、曲げ長、製造条件に依存し、電磁界シミュレーションによる確認が必要です。

== Bend90との比較

//table[06-euler-bend-t1][パラメータ・仕様一覧]{
比較項目	Bend90	EulerBend
------------------------------------------------------------
代表的な中心線	四分円	曲率が変化する曲線
曲率	円弧上で一定 @<tt>{1/R}	経路に沿って変化
直線との接続	一般に曲率が不連続	適切な設計で曲率を0から開始可能
中心線長	@<tt>{πR/2}（理想円弧）	曲線形状から算出
設計上の注意	小半径で曲げ損失	曲率ピーク・占有面積・曲線正規化
//}

== v4のパラメータ

既存の第3章に記録されている値を示します。

//table[06-euler-bend-t2][パラメータ・仕様一覧]{
パラメータ	型	初期値	単位	意味
------------------------------------------------------------
@<tt>{radius}	@<tt>{TypeDouble}	10.0	µm	v4で曲線終点を合わせるフットプリント寸法
@<tt>{width}	@<tt>{TypeDouble}	0.5	µm	導波路幅
@<tt>{points}	整数型	96	—	曲線の離散化点数に関する指定
@<tt>{layer}	@<tt>{TypeLayer}	1/0	—	導波路レイヤー
@<tt>{pin_layer}	@<tt>{TypeLayer}	2/0	—	光ポートレイヤー
//}

@<b>{重要：v4の@<tt>{radius}は、最小曲率半径そのものではありません。} 第3章で整理したとおり、生成曲線をX/Y方向にスケーリングして終点を@<tt>{(radius, radius)}に合わせる実装です。異方的なスケーリングは曲率分布を変えるため、入力値と実際の最小曲率半径を混同しないでください。

== Euler曲線の数学的原理

弧長を@<tt>{s}、曲率を@<tt>{κ(s)}とすると、理想的なEuler曲線の基本的な特徴は

//texequation{
\boxed{\kappa(s)=a s}
//}

のように曲率が弧長に比例することです（@<tt>{a}は曲率変化率）。接線角度@<tt>{θ(s)}は

//texequation{
\frac{d\theta}{ds}=\kappa(s),\qquad
\theta(s)=\theta_0+\frac{a}{2}s^2
//}

となります。始点を原点、初期接線をX軸方向とすれば、中心線座標は

//texequation{
x(s)=\int_0^s\cos\!\left(\frac{a}{2}u^2\right)du,
\qquad
y(s)=\int_0^s\sin\!\left(\frac{a}{2}u^2\right)du
//}

です。これはFresnel積分に関連します。

=== Fresnel積分

標準形は

//texequation{
C(t)=\int_0^t\cos\!\left(\frac{\pi}{2}u^2\right)du,
\qquad
S(t)=\int_0^t\sin\!\left(\frac{\pi}{2}u^2\right)du
//}

です。変数変換によってEuler曲線の座標を計算できます。

== 90°曲げを構成する方法

代表的な@<b>{対称Euler Bend}では、前半で曲率を0から最大値まで増加させ、後半で0へ減少させます。

//emlist[text]{
直線 ── 曲率増加 ── 最大曲率 ── 曲率減少 ── 直線
          κ: 0 → κmax → 0
//}

全長を@<tt>{L}とする対称な例では、

//texequation{
\kappa(s)=
\begin{cases}
a s & 0\le s\le L/2\\
a(L-s) & L/2 < s\le L
\end{cases}
//}

と定義できます。曲げ角は曲率の積分なので、

//texequation{
\Delta\theta=\int_0^L\kappa(s)ds=\frac{aL^2}{4}
//}

です。90°曲げを要求すると、

//texequation{
\Delta\theta=\frac{\pi}{2}
\quad\Rightarrow\quad
\boxed{a=\frac{2\pi}{L^2}}
//}

となります。この構成での最大曲率は

//texequation{
\kappa_{\max}=aL/2=\pi/L,
\qquad
\boxed{R_{\min}=L/\pi}
//}

です。@<b>{これは説明用の対称Euler曲線モデルに対する式であり、v4の@<tt>{radius}パラメータとの等式ではありません。}

== v4のフットプリントと曲率半径

既存のv4仕様では、終点を

//texequation{
\boxed{P_{\mathrm{end}}=(R,R)}
//}

に合わせるための座標スケーリングが用いられています（@<tt>{R = radius}）。そのため、@<tt>{radius=10 µm}のとき、終点位置は @<tt>{(10 µm, 10 µm)} と整理できます。

一方、任意の平面曲線の曲率は

//texequation{
\boxed{\kappa(t)=\frac{|x'(t)y''(t)-y'(t)x''(t)|}{\left(x'(t)^2+y'(t)^2\right)^{3/2}}}
//}

で与えられます。曲率がゼロでない箇所の曲率半径は@<tt>{R(t)=1/κ(t)}です。実際の@<tt>{R_min}を知るには、@<b>{スケーリング後の中心線}に対してこの計算を行う必要があります。微分ベクトルがゼロになる特異点にも注意が必要です。

== 数値生成の参考コード

次のコードは@<b>{v4の引用ではありません}。対称な曲率分布を弧長方向に積分し、ポリラインを生成する独立した参考実装です。返す座標はµm単位です。

//emlist[python]{
import math

def symmetric_euler_90(length_um=30.0, points=97):
    """対称Euler 90°曲げの参考点列。v4の実装そのものではない。"""
    if length_um <= 0 or points < 3:
        raise ValueError("length_um > 0, points >= 3 required")

    ds = length_um / (points - 1)
    a = 2.0 * math.pi / (length_um ** 2)

    def curvature(s):
        return a * min(s, length_um - s)

    theta = 0.0
    x, y = 0.0, 0.0
    result = [(x, y)]
    for i in range(1, points):
        s_mid = (i - 0.5) * ds
        theta_mid = theta + 0.5 * curvature(s_mid) * ds
        x += ds * math.cos(theta_mid)
        y += ds * math.sin(theta_mid)
        theta += curvature(s_mid) * ds
        result.append((x, y))
    return result

points_um = symmetric_euler_90(length_um=30.0)
# KLayoutへの挿入例（path_umは本ライブラリの共通関数を想定）:
# cell.shapes(wg_layer).insert(path_um(points_um, 0.5, layout.dbu))
//}

この例は数値積分の近似です。終点座標を@<tt>{(radius, radius)}に合わせる処理は含みません。正確な終点、接線、曲率を同時に満たすには、設計変数の調整や数値最適化が必要です。

== 離散化とDBU

曲線を@<tt>{points}個の点列にすると、KLayoutでは隣接点間が線分で接続されます。分割数が少ない場合、形状誤差や導波路長誤差が増加します。さらに、@<tt>{path_um()}でDBUへ丸める際に、異なるサンプル点が同じ整数座標になることがあります。

検証では次を確認します。

 1. 連続する点が重複していないか。
 1. 曲線の始点・終点が意図したポート位置に一致するか。
 1. 接線方向が期待する接続方向になっているか。
 1. 近似線分の長さ・角度変化が許容範囲か。
 1. DBU丸め後に自己交差や不自然な折れが発生していないか。

== 導波路長の計算

理想的な曲線長は

//texequation{
L_{\mathrm{WG}}=\int\sqrt{\left(\frac{dx}{dt}\right)^2+\left(\frac{dy}{dt}\right)^2}\,dt
//}

です。点列の場合は

//texequation{
\boxed{L_{\mathrm{poly}}=\sum_{i=0}^{N-2}\sqrt{(x_{i+1}-x_i)^2+(y_{i+1}-y_i)^2}}
//}

で計算できます。@<tt>{Bend90}の円弧長@<tt>{πR/2}を、そのまま@<tt>{EulerBend}の長さとして使うことはできません。

== 光ポートの考え方

EulerBendは2ポート導波路として扱います。v4の共通@<tt>{add_pin()}では、Pinレイヤー上の短いPathとTextでポートを表現します。@<tt>{inward_angle}は@<b>{PCell内部へ向かう方向}であり、Routerが外向き方向を用いる場合は

//texequation{
\theta_{\mathrm{out}}=(\theta_{\mathrm{in}}+180^\circ)\bmod 360^\circ
//}

で変換します。

v4の@<b>{正確な@<tt>{opt1}・@<tt>{opt2}の角度と端点座標は、公開前に@<tt>{produce_impl()}と照合してください}。図示やRouter連携では、内向き／外向きの混同を避けることが重要です。

== KLayoutでの確認手順

 1. @<tt>{Photonics}ライブラリから@<tt>{EulerBend}を選択します。
 1. @<tt>{radius=10.0}、@<tt>{width=0.5}、@<tt>{points=96}で配置します。
 1. WGレイヤー（1/0）で中心線の形状を確認します。
 1. Pinレイヤー（2/0）で@<tt>{opt1}・@<tt>{opt2}の位置と方向を確認します。
 1. @<tt>{radius}を変更し、フットプリントと曲線形状がどう変わるか比較します。
 1. @<tt>{points}を変更し、表示形状とDBU丸めの影響を確認します。

※ 光損失の評価にはKLayout上の形状確認とは別に光学シミュレーションが必要です。

== Photonics Router v6.xとの連携

RouterがEulerBendをインスタンスとして扱う場合、@<b>{配置変換後のポート座標と方向}を取得し、接続先と照合します。曲げ部分の導波路長をネットリストに記録する場合、v4の@<tt>{radius}から円弧長を推定せず、@<b>{実際の生成中心線から長さを算出}する必要があります。

推奨する検証項目は次のとおりです。

 * インスタンス回転・反転後のポート位置と角度
 * 接続部の位置誤差と導波路幅の一致
 * 最小曲率半径と接線連続性
 * 導波路長の計算精度
 * 光ポートとNetlist端子の対応

== PCell Library v5への改善案

//table[06-euler-bend-t3][パラメータ・仕様一覧]{
改善項目	提案
------------------------------------------------------------
パラメータ名	フットプリント寸法と最小曲率半径を区別する
曲率検証	生成後の@<tt>{R_min}を算出して設計制約を確認
曲線生成	真の対称Euler曲線などの方式を明示
精度管理	点数だけでなく最大弦誤差を指定可能にする
ポート仕様	位置・幅・方向を共通メタデータ化
導波路長	中心線長を計算してRouterへ提供
パラメータ検証	負値、極小寸法、丸めによる退化を検出
//}

== まとめ

@<tt>{EulerBend}は、曲率が徐々に変化する導波路形状を扱うPCellです。v4の@<tt>{radius}は終点フットプリントに関連する値であり、@<b>{最小曲率半径を直接保証しない}点が重要です。Bend90との違いを理解し、曲率分布・導波路長・ポート方向を検証することで、Router連携と次世代PCellへの拡張が容易になります。

@<b>{次章：第7章 SBend — S字導波路}


=== PCell構造図（v4初期パラメータ）

//image[06-euler-bend-1][06_euler_bend の中心線・MMI領域・Optical Port][scale=0.8]{
//}

@<i>{青：導波路中心線、淡青：MMI領域、橙矢印：@<tt>{add_pin()} の内向き方向。図はPython実装の座標式に基づく概念図であり、KLayoutのGDSレンダリングではありません。}
