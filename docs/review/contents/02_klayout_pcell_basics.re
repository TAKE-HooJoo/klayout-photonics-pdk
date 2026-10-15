= KLayoutとPCellの基本

== PCellの概念

PCellは、同じ種類の図形をパラメータから生成するセルです。例えばStraightでは、@<tt>{length}と@<tt>{width}を変えることで、異なる長さ・幅の導波路を同じPCell定義から生成できます。

KLayoutのPython PCellは、@<tt>{pya.PCellDeclarationHelper}を継承して作成できます。

//emlist[python]{
class Straight(pya.PCellDeclarationHelper):
    def __init__(self):
        super(Straight, self).__init__()
        self.param("length", self.TypeDouble, "Length (um)", default=100.0)
        self.param("width", self.TypeDouble, "Width (um)", default=0.5)

    def produce_impl(self):
        # レイアウト図形の生成処理
        pass
//}

上記はAPIの最小構成を説明する@<b>{簡略例}です。実際のv4では、共通の@<tt>{Base}クラスを継承し、導波路レイヤーとPinレイヤーも登録します。

== PCellの生成サイクル

 1. PCellクラスを宣言する。
 1. @<tt>{self.param()}でパラメータを定義する。
 1. @<tt>{produce_impl()}に形状生成処理を書く。
 1. @<tt>{layout.register_pcell()}でライブラリに登録する。
 1. KLayoutでPCellインスタンスを配置し、パラメータを指定する。

@<tt>{produce_impl()}では、@<tt>{self.layout}と@<tt>{self.cell}を通して、図形を配置する対象レイアウト・セルにアクセスします。

== レイヤー

v4の標準レイヤー定義は次のとおりです。

//emlist[python]{
WG_LAYER  = pya.LayerInfo(1, 0)
PIN_LAYER = pya.LayerInfo(2, 0)
//}

//table[02-klayout-pcell-basics-t1][パラメータ・仕様一覧]{
レイヤー	用途
------------------------------------------------------------
1/0	光導波路の形状
2/0	光ポートのPathとText
//}

これはv4の@<b>{ライブラリ内での初期設定}です。特定ファウンドリの製造レイヤー番号であることを保証しません。

== DBUと座標変換

KLayoutの@<tt>{pya.Point}や@<tt>{pya.Path}では整数のDBU座標を使用します。v4には、µm単位の値をDBUへ変換する関数があります。

//emlist[python]{
def q(v, dbu):
    return int(round(v / dbu))
//}

例えばDBUが0.001 µmの場合、10 µmは10,000 DBUです。

//texequation{
N_{\mathrm{DBU}}=\operatorname{round}\left(\frac{x_{\mu m}}{\mathrm{DBU}}\right)
//}

@<b>{注意：} DBUへの丸めにより、微小な座標誤差が生じます。曲線の分割点数や細い導波路の幅は、使用するDBUに対して適切に設定する必要があります。

== Pathによる導波路生成

v4では、導波路の中心線を点列で定義し、@<tt>{pya.Path}に変換します。

//emlist[python]{
def path_um(points, width, dbu):
    return pya.Path(
        [pya.Point(q(x, dbu), q(y, dbu)) for x, y in points],
        q(width, dbu)
    )
//}

例えば、

//emlist[python]{
path_um([(0, 0), (20, 0)], 0.5, layout.dbu)
//}

は、中心線が(0,0)から(20,0)までの直線で、幅0.5 µmのPathを作ります。@<tt>{Path}の幾何学的な端部形状はKLayoutのPath仕様に従います。

== BoxによるMMI本体の生成

MMIのような矩形領域は@<tt>{pya.Box}で生成します。

//emlist[python]{
pya.Box(
    q(xmin, layout.dbu), q(ymin, layout.dbu),
    q(xmax, layout.dbu), q(ymax, layout.dbu)
)
//}

@<tt>{Box}は長方形の幾何学形状であり、光学的な自己結像条件や結合効率を計算する機能ではありません。

== Bézier曲線のサンプリング

v4では3次Bézier曲線を点列に離散化する@<tt>{bezier()}関数を使用します。

//texequation{
B(t)=(1-t)^3P_0+3(1-t)^2tP_1+3(1-t)t^2P_2+t^3P_3,
\quad 0\leq t\leq1
//}

制御点@<tt>{P0}～@<tt>{P3}によって端点と接線方向を調整できます。生成した点列は@<tt>{path_um()}で導波路図形に変換します。

@<b>{注意：} 曲線の端点で接線が一致しても、曲率が連続するとは限りません。また、制御点の距離は必ずしも最小曲率半径に一致しません。

== 光ポートの表現

v4では、@<tt>{add_pin()}がPinレイヤー上に短いPathとポート名Textを生成します。

//emlist[python]{
add_pin(cell, layout, pin_layer, "opt1", x, y, inward_angle, width)
//}

@<tt>{inward_angle}は@<b>{ポートからセル内部へ向かう方向}です。Routerで外向き方向を使う場合には、次の変換が必要です。

//texequation{
\theta_{\mathrm{out}}=(\theta_{\mathrm{in}}+180^\circ)\bmod360^\circ
//}

v4の光ポートは、位置・方向・名前をレイアウト図形として表現したものです。独立したネットリスト接続オブジェクトが自動生成されるわけではありません。

== PCellインスタンスの変換

PCellインスタンスは、配置時に平行移動、回転、反転できます。Routerが接続先を判定するときは、@<b>{PCellローカル座標のポート情報を、インスタンス変換後の座標へ変換}する必要があります。

== 確認事項

KLayoutでPCellを使用する際には、以下を確認します。

 * マクロが読み込まれ、@<tt>{Photonics}ライブラリが表示されること
 * パラメータ変更で形状が再生成されること
 * 導波路レイヤーとPinレイヤーが意図どおりであること
 * ポートの位置と方向が図形の端点に一致すること
 * 生成された形状が対象プロセスの設計ルールに適合すること



@<b>{参照:} v4マクロ（GitHub） (https://github.com/TAKE-HooJoo/klayout-photonics-pdk/blob/main/pymacros/photonics_pdk_v4.lym)
