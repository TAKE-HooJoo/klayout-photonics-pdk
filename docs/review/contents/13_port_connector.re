= PortConnector — 光ポート接続・位置合わせ

@<b>{対象ソース:} @<tt>{pymacros/photonics_pdk_v4.lym}、@<tt>{PortConnector} クラス（v4）  
@<b>{文書状態:} ソースコード照合済み（2026-10-15）  
@<b>{参照:} https://github.com/TAKE-HooJoo/klayout-photonics-pdk/blob/main/pymacros/photonics_pdk_v4.lym

== 概要

@<tt>{PortConnector} は、@<b>{短い直線導波路と、名前付きの2つの光ポート}を生成する位置合わせ用PCellである。光ポートの可視化、接続位置の確認、Routerの動作試験などに利用できる。

v4の実装では @<tt>{Straight} と幾何形状・ポート生成処理がほぼ同じであり、特別な自動スナップ機構や、2つの既存PCellインスタンスを探索して接続する機能は持たない。「Connector」という名称は@<b>{接続補助用の短い直線PCell}という意味で理解する。

== 形状と座標

//emlist[text]{
             +X →

  opt1                         opt2
  (0,0)                      (length,0)
    ●══════════════════════════●
    →                          ←
  inward 0°                inward 180°

      中心線 y = 0、幅 width
//}

 * 中心線：@<tt>{(0, 0)} から @<tt>{(length, 0)}
 * 導波路幅：@<tt>{width}
 * 光ポート：左端 @<tt>{opt1}、右端 @<tt>{opt2}
 * デフォルトでは @<tt>{length=10.0 µm}、@<tt>{width=0.5 µm}

形状は波導レイヤー上の @<tt>{pya.Path} として生成される。

== PCellパラメータ

//table[13-port-connector-t1][パラメータ・仕様一覧]{
パラメータ	型	初期値	単位	役割
------------------------------------------------------------
@<tt>{length}	@<tt>{TypeDouble}	10.0	µm	接続補助導波路の中心線長
@<tt>{width}	@<tt>{TypeDouble}	0.5	µm	導波路幅
@<tt>{layer}	@<tt>{TypeLayer}	@<tt>{(1, 0)}	—	導波路の描画レイヤー
@<tt>{pin_layer}	@<tt>{TypeLayer}	@<tt>{(2, 0)}	—	光ポートの描画レイヤー
//}

@<tt>{layer} と @<tt>{pin_layer} は @<tt>{Base.layers()} によって共通定義される。

== v4の実装

次の抜粋は @<tt>{PortConnector} クラスの実装である。

//emlist[python]{
class PortConnector(Base):
    """Visible alignment helper: a short waveguide with two named optical ports."""
    def __init__(self):
        super(PortConnector,self).__init__()
        self.param("length",self.TypeDouble,"Connector length (um)",default=10.0)
        self.param("width",self.TypeDouble,"Width (um)",default=0.5)
        self.layers()

    def produce_impl(self):
        l,c=self.layout,self.cell; wg=l.layer(self.layer); pin=l.layer(self.pin_layer)
        c.shapes(wg).insert(path_um([(0,0),(self.length,0)],self.width,l.dbu))
        add_pin(c,l,pin,"opt1",0,0,0,self.width)
        add_pin(c,l,pin,"opt2",self.length,0,180,self.width)
//}

=== 処理の流れ

 1. @<tt>{__init__()} で長さ・幅・共通レイヤーを宣言する。
 1. @<tt>{produce_impl()} で導波路レイヤーとPinレイヤーを取得する。
 1. @<tt>{path_um()} で中心線をKLayoutのDBU整数座標へ変換し、@<tt>{pya.Path} を挿入する。
 1. @<tt>{add_pin()} で両端に光ポートを作成する。

== Optical Portの仕様

//table[13-port-connector-t2][パラメータ・仕様一覧]{
名前	ローカル位置（µm）	内向き角度	ポート幅
------------------------------------------------------------
@<tt>{opt1}	@<tt>{(0, 0)}	0°（+X）	@<tt>{width}
@<tt>{opt2}	@<tt>{(length, 0)}	180°（−X）	@<tt>{width}
//}

@<tt>{add_pin()} はPinレイヤーに@<b>{短いPathとポート名のText}を挿入する。既定のPin Path長は @<tt>{1.0 µm} であり、端点からPCell内部へ向けて描かれる。Pin Pathは導波路レイヤーとは別レイヤーに置かれる。

@<b>{注意：} 角度はポートの@<b>{内向き}方向を示す。外部の接続先へ向かう方向として扱う場合は180°反転が必要である。Router側のポート抽出仕様と必ず照合する。

== Straightとの比較

//table[13-port-connector-t3][パラメータ・仕様一覧]{
項目	@<tt>{Straight}	@<tt>{PortConnector}
------------------------------------------------------------
初期長さ	100 µm	10 µm
初期幅	0.5 µm	0.5 µm
中心線形状	直線	直線
光ポート	@<tt>{opt1}, @<tt>{opt2}	@<tt>{opt1}, @<tt>{opt2}
ポート角度	0° / 180°	0° / 180°
主な想定用途	一般の直線導波路	接続位置合わせ・テスト
//}

@<b>{実装上の主な違いは初期長さと用途を表す名称である。} @<tt>{PortConnector} 固有の接続判定アルゴリズムはない。

== 導波路長と光学位相

導波路中心線長は単純に

//texequation{
L=\texttt{length}
//}

である。単一モード・一様断面の近似では、波長 \(\lambda\)、実効屈折率 \(n_\mathrm{eff}\) に対する位相遅延は

//texequation{
\phi=\beta L=\frac{2\pi n_\mathrm{eff}}{\lambda}L
//}

となる。これは光学設計上の理論式であり、PCell自体は \(n_\mathrm{eff}\) や位相を計算しない。

== KLayoutでの確認手順

 1. @<tt>{photonics_pdk_v4.lym} をKLayoutで読み込み、@<tt>{Photonics} ライブラリが登録されていることを確認する。
 1. PCell一覧から @<tt>{PortConnector} を選択する。
 1. @<tt>{length=10.0}、@<tt>{width=0.5} のまま配置する。
 1. レイヤー @<tt>{(1,0)} に長さ10 µmの導波路が描画されていることを確認する。
 1. レイヤー @<tt>{(2,0)} を表示し、両端の @<tt>{opt1} / @<tt>{opt2} のラベルと短いPin Pathを確認する。
 1. 長さを変更し、右側の @<tt>{opt2} が指定したX座標へ移動することを確認する。

== Photonics Router v6.xとの連携

@<tt>{PortConnector} は、ポート抽出機能のテストに適した単純な2ポート素子である。たとえば、2つの @<tt>{PortConnector} インスタンスを離して配置し、Routerがポートの座標・方向・幅・インスタンス変換を正しく解釈できるか検証できる。

ただし、以下の点は@<b>{Router側の実装依存}である。

 * Pinレイヤー上のTextとPathからのポート認識方法
 * 回転・反転したインスタンスのポート座標変換
 * 内向き角度とルーティング出発方向の対応
 * 接続後の導波路長計算とネットリスト抽出

@<tt>{PortConnector} を配置するだけで自動接続やネットリスト生成が実行されるわけではない。

== 設計上の注意点

 * @<b>{長さ・幅の検証:} v4のこのPCellには、負値やゼロ値を明示的に拒否する入力チェックがない。運用上は @<tt>{length > 0}、@<tt>{width > 0} を前提とする。
 * @<b>{DBU丸め:} @<tt>{q(v, dbu) = int(round(v / dbu))} により座標・幅が整数DBUに丸められる。非常に小さい寸法では丸め誤差に注意する。
 * @<b>{レイヤーの分離:} Pin Pathは光導波路本体の形状ではない。描画や検証でPinレイヤーを導波路と混同しない。
 * @<b>{ポートの向き:} 左端は+X、右端は−Xが「内向き」であり、導波路の伝搬方向や外向き法線とは必ずしも同じではない。
 * @<b>{自動接続ではない:} インスタンス間の幾何学的接続や衝突回避は別途Router等で行う。

== v5への改善案（未実装）

 1. @<tt>{length}、@<tt>{width} に対する正値チェックを追加する。
 1. ポートの中心位置・方向・幅を、テキストとPin Pathに加えて構造化メタデータとして扱う。
 1. @<tt>{Straight} と重複する実装を共通クラスまたはユーティリティへ整理する。
 1. 接続許容誤差、幅の一致、ポート方向の整合性を検証する機能をRouter側と協調して追加する。
 1. 回転・ミラー・階層インスタンスを含む自動テストを整備する。

これらは提案であり、v4で実装済みの機能ではない。

== まとめ

@<tt>{PortConnector} は、@<b>{短い直線導波路＋2つの名前付き光ポート}という最小構成のPCellである。初期長さ10 µmで、光ポートの表示、位置合わせ、Photonics Routerのポート抽出試験に適している。一方、v4には自動スナップや自動接続機能はない。設計時はポートの内向き角度、Pinレイヤー、DBU丸めを正しく理解して利用する。


=== PCell構造図（v4初期パラメータ）

//image[13-port-connector-1][13_port_connector の中心線・MMI領域・Optical Port][scale=0.8]{
//}

@<i>{青：導波路中心線、淡青：MMI領域、橙矢印：@<tt>{add_pin()} の内向き方向。図はPython実装の座標式に基づく概念図であり、KLayoutのGDSレンダリングではありません。}
