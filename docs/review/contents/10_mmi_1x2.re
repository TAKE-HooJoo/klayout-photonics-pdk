= MMI_1x2 — 多モード干渉型1×2光分岐器

@<b>{対象実装:} @<tt>{pymacros/photonics_pdk_v4.lym} の @<tt>{class MMI1x2(Base)}（ライブラリ登録名 @<tt>{MMI_1x2}）  
@<b>{確認日:} 2026-10-15  
@<b>{対象:} KLayout Silicon Photonics PDK v4

== 概要と用途

@<tt>{MMI_1x2} は、幅の広い多モード導波路領域（MMI本体）と、左側の入力導波路1本、右側の出力導波路2本からなる@<b>{1入力2出力のレイアウトPCell}である。光分岐器、MZIの入力分岐部、干渉回路などの構成要素として利用できる。

@<b>{重要:} v4は幾何形状と光ポートを生成する。50:50分岐比、挿入損失、帯域幅などの光学性能は計算・保証しない。MMI寸法はモード解析、EME/FDTDなどで別途設計・検証する必要がある。

== 構造と座標系

//emlist[text]{
                            y ↑
                              │
                              │      opt2 ●  (X,+d/2)
                              │    ┌───────┘
opt1 ●─────────┌──────────────┤
(0,0)         │   MMI 本体   │
              │              ├───────┐
              └──────────────┘       ●  opt3 (X,-d/2)
              x=a            x=a+L   x=X=2a+L  → x

MMI本体: x∈[a,a+L], y∈[-W/2,+W/2]
入力導波路: (0,0) → (a,0)
上側出力:   (a+L,+d/2) → (X,+d/2)
下側出力:   (a+L,-d/2) → (X,-d/2)
//}

この図は接続関係を示す概念図であり、実際のMMI本体は単一の矩形 @<tt>{pya.Box}、アクセス導波路は3本の @<tt>{pya.Path} で構成される。@<tt>{a=access_length}、@<tt>{L=mmi_length}、@<tt>{W=mmi_width}、@<tt>{d=port_spacing} とする。

== PCellパラメータ

//table[10-mmi-1x2-t1][パラメータ・仕様一覧]{
パラメータ	型	v4初期値	意味
------------------------------------------------------------
@<tt>{wg_width}	@<tt>{TypeDouble}	0.5 µm	入出力アクセス導波路の幅
@<tt>{mmi_width}	@<tt>{TypeDouble}	4.0 µm	MMI本体の幅（y方向）
@<tt>{mmi_length}	@<tt>{TypeDouble}	20.0 µm	MMI本体の長さ（x方向）
@<tt>{port_spacing}	@<tt>{TypeDouble}	2.0 µm	出力2ポートの中心間隔
@<tt>{access_length}	@<tt>{TypeDouble}	5.0 µm	入力・出力アクセス導波路の長さ
@<tt>{layer}	@<tt>{TypeLayer}	(1, 0)	導波路レイヤー（共通@<tt>{Base}）
@<tt>{pin_layer}	@<tt>{TypeLayer}	(2, 0)	光ポートレイヤー（共通@<tt>{Base}）
//}

初期値では全長は @<tt>{X = 2×5+20 = 30 µm}、MMI本体は @<tt>{x=5〜25 µm}、@<tt>{y=-2〜+2 µm}、出力中心は @<tt>{y=±1 µm} となる。

== Python実装の解説

以下はv4ソースの処理を、変数名と構造を維持して読みやすく整形した抜粋である。

//emlist[python]{
class MMI1x2(Base):
    def __init__(self):
        super(MMI1x2, self).__init__()
        self.param("wg_width", self.TypeDouble, "WG width (um)", default=0.5)
        self.param("mmi_width", self.TypeDouble, "MMI width (um)", default=4.0)
        self.param("mmi_length", self.TypeDouble, "MMI length (um)", default=20.0)
        self.param("port_spacing", self.TypeDouble, "Output spacing (um)", default=2.0)
        self.param("access_length", self.TypeDouble, "Access length (um)", default=5.0)
        self.layers()

    def produce_impl(self):
        l, c = self.layout, self.cell
        wg = l.layer(self.layer)
        pin = l.layer(self.pin_layer)
        a = self.access_length
        L = self.mmi_length
        y = self.port_spacing / 2

        c.shapes(wg).insert(
            pya.Box(q(a, l.dbu), q(-self.mmi_width / 2, l.dbu),
                    q(a + L, l.dbu), q(self.mmi_width / 2, l.dbu))
        )
        c.shapes(wg).insert(path_um([(0, 0), (a, 0)], self.wg_width, l.dbu))
        c.shapes(wg).insert(path_um([(a + L, y), (2*a + L, y)], self.wg_width, l.dbu))
        c.shapes(wg).insert(path_um([(a + L, -y), (2*a + L, -y)], self.wg_width, l.dbu))

        add_pin(c, l, pin, "opt1", 0, 0, 0, self.wg_width)
        add_pin(c, l, pin, "opt2", 2*a + L, y, 180, self.wg_width)
        add_pin(c, l, pin, "opt3", 2*a + L, -y, 180, self.wg_width)
//}

 * @<tt>{q(value, dbu)} は µm 値を @<tt>{round(value/dbu)} により整数DBUへ変換する。
 * @<tt>{pya.Box} はMMIの矩形領域を生成する。
 * @<tt>{path_um} はアクセス導波路の中心線と幅から @<tt>{pya.Path} を生成する。
 * @<tt>{add_pin} はPinレイヤー上に短いPathとポート名Textを作成する。
 * Pythonクラス名は @<tt>{MMI1x2}、KLayoutのPCell登録名は @<tt>{MMI_1x2} であり、表記が異なる。

== Optical Portの仕様

//table[10-mmi-1x2-t2][パラメータ・仕様一覧]{
ポート	位置 (µm)	初期値の位置 (µm)	内向き角度	用途
------------------------------------------------------------
@<tt>{opt1}	@<tt>{(0, 0)}	@<tt>{(0, 0)}	0°	入力側
@<tt>{opt2}	@<tt>{(2a+L, +d/2)}	@<tt>{(30, +1)}	180°	上側出力
@<tt>{opt3}	@<tt>{(2a+L, -d/2)}	@<tt>{(30, -1)}	180°	下側出力
//}

@<tt>{add_pin} の角度は@<b>{素子内部へ向かう方向}である。ポートの向きは接続判定に利用できるが、v4のPinは @<tt>{pya.Text} と短い @<tt>{pya.Path} であり、独立した構造化ポートオブジェクトではない。Router側ではレイヤー、ラベル、方向を正しく読み取る必要がある。

== MMIの光学原理（設計背景）

MMI領域では複数の横モードが伝搬し、それぞれの伝搬定数の差により干渉パターンが変化する。適切な長さでは入力場の複数像が形成され、2本の出力導波路に光を取り出せる（@<b>{自己結像}）。

モード間の位相差は概念的に

//texequation{
\Delta\phi_{mn}(L)=(\beta_m-\beta_n)L
//}

で表される。ここで @<tt>{β_m} と @<tt>{β_n} は各モードの伝搬定数である。必要なMMI長は有効幅、波長、偏波、材料、導波路断面、励起モードなどに依存するため、@<b>{@<tt>{mmi_length=20 µm} が一般に50:50分岐を意味するわけではない}。

MMIの分岐比はアクセス導波路の出力位置やモード重なりにも依存する。幾何学的に対称な出力配置は左右対称性を与えるが、低損失・高均等性の十分条件ではない。

== 寸法条件と幾何学的な注意点

 1. @<tt>{wg_width > 0}、@<tt>{mmi_width > 0}、@<tt>{mmi_length > 0}、@<tt>{access_length > 0} が基本的な前提となる。
 1. 出力アクセス導波路をMMI矩形の上下端からはみ出させないための単純な条件は @<tt>{port_spacing/2 + wg_width/2 ≤ mmi_width/2}、すなわち @<tt>{port_spacing + wg_width ≤ mmi_width} である。ただしこれは光学的最適化条件ではない。
 1. 出力2本を幾何学的に離すには @<tt>{port_spacing ≥ wg_width} が目安となる。ギャップを設ける場合はより大きな間隔が必要。
 1. v4の実装には、これらの値を自動検証する @<tt>{coerce_parameters_impl()} 等の処理は見当たらない。無効な寸法設定は利用者側で回避する必要がある。
 1. MMI本体とアクセス導波路は別Shapeとして挿入される。レイアウト表示上の接続と、製造用マスクのブール演算・DRC結果は区別する。

== KLayoutでの確認手順

 1. @<tt>{photonics_pdk_v4.lym} をKLayoutのPythonマクロとして読み込み、ライブラリ @<tt>{Photonics} が登録されていることを確認する。
 1. ライブラリ内の @<tt>{MMI_1x2} を配置する。
 1. 初期値で矩形本体（x=5〜25 µm、y=±2 µm）と3本のアクセス導波路を確認する。
 1. 導波路レイヤー @<tt>{(1,0)} とPinレイヤー @<tt>{(2,0)} を表示する。
 1. @<tt>{opt1}、@<tt>{opt2}、@<tt>{opt3} のラベルと座標・向きを確認する。
 1. @<tt>{port_spacing} と @<tt>{mmi_width} を変更し、矩形境界と出力導波路の位置関係を確認する。

== Photonics Router v6.xとの連携

MMIは1入力2出力の分岐点である。Routerが光ポートを抽出する際は、@<b>{インスタンス変換後のグローバル座標}とポート方向を扱う必要がある。特にミラー・回転配置したMMIでは、ローカル座標の @<tt>{±d/2} と接続先の上下関係が入れ替わり得る。

また、@<tt>{opt1}→@<tt>{opt2}、@<tt>{opt1}→@<tt>{opt3} は@<b>{2つの別経路}であり、光ネットリストでは分岐器の3ポート接続関係を保つ必要がある。v4のPCell単体は分岐比やSパラメータを提供しないため、Routerによるネットリスト抽出と光学回路シミュレーションを混同しない。

== v5への改善案（現行v4には未実装）

 * @<tt>{coerce_parameters_impl()} 等で寸法の妥当性を検査する。
 * 入出力テーパーをパラメータ化し、MMI本体との遷移を設計できるようにする。
 * 波長・偏波・プロセス別の検証済みMMI寸法をプリセット化する。
 * ポートを構造化メタデータとして保持し、Router・ネットリスト抽出に渡す。
 * EMシミュレーションで得たSパラメータモデルを関連付ける。
 * DRCチェック、最小ギャップ、レイヤー構成を製造プロセスのPDKルールと連携させる。

== まとめ

@<tt>{MMI_1x2} は、矩形MMI領域、1本の入力アクセス導波路、2本の出力アクセス導波路、および3つの名前付き光ポートを生成するPCellである。初期形状の全長は30 µmで、出力ポート中心は @<tt>{(30,+1)} と @<tt>{(30,-1)} µmに位置する。@<b>{この幾何形状は光学特性の保証を意味しない}ため、設計には電磁界解析とプロセス条件に基づく検証が必要である。



@<b>{実装参照:} @<tt>{pymacros/photonics_pdk_v4.lym}、@<tt>{class MMI1x2(Base)}、PCell登録名 @<tt>{MMI_1x2}。GitHubの@<tt>{main}は更新される可能性があるため、正式版では参照コミットを固定する。


=== PCell構造図（v4初期パラメータ）

//image[10-mmi-1x2-1][10_mmi_1x2 の中心線・MMI領域・Optical Port][scale=0.8]{
//}

@<i>{青：導波路中心線、淡青：MMI領域、橙矢印：@<tt>{add_pin()} の内向き方向。図はPython実装の座標式に基づく概念図であり、KLayoutのGDSレンダリングではありません。}
