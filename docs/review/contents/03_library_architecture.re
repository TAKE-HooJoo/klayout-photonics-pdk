= PCell Library v4のアーキテクチャ

== ファイル構造

v4の実装は、KLayoutマクロファイル@<tt>{photonics_pdk_v4.lym}にまとめられています。ファイルはXML形式で、@<tt>{<text>}要素にPythonコードを格納しています。

//emlist[text]{
photonics_pdk_v4.lym
├── XMLマクロ設定（Python / autorun）
└── Pythonコード
    ├── レイヤー定義
    ├── 共通幾何学関数（q, path_um, bezier）
    ├── 光ポート生成関数（add_pin）
    ├── 共通Baseクラス
    ├── 10種類のPCellクラス
    └── PhotonicsLibrary（登録処理）
//}

== 共通関数

//table[03-library-architecture-t1][パラメータ・仕様一覧]{
関数	役割
------------------------------------------------------------
@<tt>{q(v, dbu)}	µm値を整数DBUに変換
@<tt>{path_um(points, width, dbu)}	点列からPathを生成
@<tt>{bezier(p0, p1, p2, p3, n)}	3次Bézier曲線を点列化
@<tt>{add_pin(...)}	PinレイヤーにPathとTextを生成
//}

これらの関数は複数のPCellから呼び出され、図形生成方法を共通化しています。

== Baseクラス

v4のBaseクラスは、各PCellに共通する2つのレイヤーパラメータを定義します。

//emlist[python]{
class Base(pya.PCellDeclarationHelper):
    def layers(self):
        self.param("layer", self.TypeLayer,
                   "Waveguide layer", default=WG_LAYER)
        self.param("pin_layer", self.TypeLayer,
                   "Optical pin layer", default=PIN_LAYER)
//}

各PCellは@<tt>{Base}を継承し、コンストラクタで@<tt>{self.layers()}を呼び出します。

== PCellクラスの登録

ライブラリ登録処理では、次の10種類の名前が使用されます。

//emlist[python]{
class PhotonicsLibrary(pya.Library):
    def __init__(self):
        self.description = "Simple Silicon Photonics PCell Library v4"
        z = self.layout()
        for name, pc in [
            ("Straight", Straight()),
            ("Bend90", Bend90()),
            ("EulerBend", EulerBend()),
            ("SBend", SBend()),
            ("Ring", Ring()),
            ("DirectionalCoupler", DirectionalCoupler()),
            ("MMI_1x2", MMI1x2()),
            ("MZI", MZI()),
            ("WaveguideRoute", WaveguideRoute()),
            ("PortConnector", PortConnector())
        ]:
            z.register_pcell(name, pc)
        self.register("Photonics")

PhotonicsLibrary()
//}

上記はv4の登録部分を@<b>{整形して掲載}したものです。ライブラリ名は@<tt>{Photonics}で、@<tt>{MMI_1x2}の内部Pythonクラス名は@<tt>{MMI1x2}です。

== 全PCellの初期パラメータ

//table[03-library-architecture-t2][パラメータ・仕様一覧]{
PCell	主要パラメータ（初期値、µm。ただしpointsは無次元）	光ポート数
------------------------------------------------------------
Straight	length=100, width=0.5	2
Bend90	radius=10, width=0.5, points=64	2
EulerBend	radius=10, width=0.5, points=96	2
SBend	length=20, offset=5, width=0.5, points=64	2
Ring	radius=10, width=0.5, gap=0.2, bus_length=40, points=128	2
DirectionalCoupler	coupling_length=20, access_length=15, gap=0.2, port_spacing=5, width=0.5	4
MMI_1x2	wg_width=0.5, mmi_width=4, mmi_length=20, port_spacing=2, access_length=5	3
MZI	mmi_width=4, mmi_length=20, access_length=5, arm_length=80, arm_spacing=10, sbend_length=20, width=0.5	2
WaveguideRoute	dx=100, dy=20, width=0.5, radius=10, points=24	2
PortConnector	length=10, width=0.5	2
//}

@<b>{共通パラメータ:} 全PCellで@<tt>{layer=1/0}、@<tt>{pin_layer=2/0}を指定できます。

== 生成処理の共通パターン

ほとんどのPCellは、次の処理を実行します。

//emlist[text]{
PCellパラメータ
     ↓
中心線または矩形の座標計算
     ↓
DBU変換
     ↓
WGレイヤーへ図形を挿入
     ↓
Pinレイヤーへ光ポートを挿入
     ↓
PCellインスタンスとして配置
//}

この構造は理解しやすく、個別のPCellを拡張しやすい利点があります。

== 設計上の特徴と制約

=== 光ポートはPath＋Text

各PCellは@<tt>{add_pin()}を使用します。ポート名は@<tt>{opt1}、@<tt>{opt2}などです。ただし、ポートメタデータが別の構造化データとして保持されるわけではありません。

=== 曲線は離散点列

円弧・Bézier曲線・Euler型曲線は点列として生成され、@<tt>{pya.Path}へ変換されます。分割数とDBUが形状精度に影響します。

=== EulerBendのradiusの解釈

v4の@<tt>{EulerBend}では、生成した曲線をX/Y方向にスケーリングして終点を@<tt>{(radius, radius)}に合わせています。したがって、パラメータ名の@<tt>{radius}は@<b>{フットプリント寸法の指定}であり、厳密な最小曲率半径を保証する値ではありません。

=== WaveguideRouteのradiusの解釈

v4の@<tt>{WaveguideRoute}では、@<tt>{radius}をBézier曲線の制御距離の計算に使用します。@<b>{実際の曲線の最小曲率半径が@<tt>{radius}になるわけではありません。}

=== MZIの対称性

MZIの下側アームは、上側アームのY座標を反転して生成しています。したがって、中心線の幾何学的長さは上下で等しく、v4には意図的な光路長差を与えるパラメータはありません。

=== PortConnectorの役割

PortConnectorは、短い直線導波路と2つの光ポートを生成します。外部PCellのポートを探索する自動接続アルゴリズムは実装されていません。

== Photonics Routerとの役割分担

//table[03-library-architecture-t3][パラメータ・仕様一覧]{
PCell Library v4	Photonics Router（連携対象）
------------------------------------------------------------
部品内部の図形を生成	配置済み部品のポートを検出
パラメータから形状を生成	ポート間の経路を計算
Pinレイヤーにポートを記述	回転・反転後のポート座標を扱う
個々の光デバイスを表現	部品間の接続関係を抽出
//}

Routerの具体的な機能・実装状態は、対象バージョンのRouterソースコードを別途確認して記載します。

== 将来の改善候補

 1. ポート座標・角度・幅・名前を共通仕様で管理する。
 1. 曲線の最小曲率半径を数値的に検証する。
 1. 導波路中心線長を統一的に計算する。
 1. PCellのパラメータ妥当性チェックを追加する。
 1. 光学性能の推定値と、電磁界シミュレーションによる検証結果を区別して記録する。
 1. 参照コミットIDとKLayoutバージョンを解説書に固定する。

== まとめ

Photonics PDK v4は、共通の幾何学関数と光ポート生成関数を利用する10種類のPCellから構成されています。現状の中心機能は@<b>{パラメトリックなレイアウト生成}です。今後、Photonics Routerとの統合や光学検証を進めるには、ポート情報・曲率検証・導波路長の共通化が重要です。



@<b>{参照:} v4マクロ（GitHub） (https://github.com/TAKE-HooJoo/klayout-photonics-pdk/blob/main/pymacros/photonics_pdk_v4.lym)
