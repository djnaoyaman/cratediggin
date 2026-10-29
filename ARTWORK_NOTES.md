# グラフィティ制作ノート

2026年10月17日決定。今後の画像・楽曲追加でも自動的に適用する。

## 品質と配色

承認された Mass Appeal の試作を基準に、文字の骨格、重なり、余白、飛沫、塗料の垂れ、かすれを曲ごとに構成する。曲名・アーティスト名と版名を正確に残す。既存ライターの署名や作品を転載・模倣しない。

色は作品ジャケットを参照する。UIの青と作品の配色を分け、`paletteSource` と `paletteNote` に根拠と目視解釈の範囲を記録する。未照合の共通色をジャケット由来と表示しない。

## 透過と壁

画像は真のアルファ付き透過。紙の白地・開いた余白を抜き、文字内の白い塗りは残す。矩形、マット、壁、チェック柄、影を画像に含めない。WebP化してもアルファを保持する。

壁の凹凸、目地、汚れと描かれる演出はサイト側で扱う。動きを減らす設定では完成状態を表示する。

## alt の自動生成

形式は `曲名 — アーティスト名｜CRATE DIGGIN｜DJ Naoyaman`。

例 `Mass Appeal — Gang Starr｜CRATE DIGGIN｜DJ Naoyaman`。

`build.py` が曲データから自動生成し、静的HTMLと全画面表示に適用する。曲切り替えでも更新する。共有用楽曲画像の説明にも同形式を使う。画像自体へこの文字列を描き足す指示ではない。

## 検証と公開単位

`graffiti_artwork.json` に進捗を記録する。文字、色、欠け、実際のアルファと完全なデコードを確認してから ready にする。ファイル変換は一時ファイルへ出力し、検証後にアトミックに保存する。

制作・公開は40曲などの固定件数で区切らず、生成サービス・実行環境・保存先の利用可能な範囲で、品質検証できる最大限の件数を進める。残り枠を取得できない場合は推測値を断定しない。各画像の完成ごとに保存し、上限や失敗を検知した場合は追加生成を止め、検証済みの成果をまとめて公開する。 対象曲数はtracks.jsonを正本とする。ソースと画像をGitに保存し、本番デプロイ成功を確認する。

`python build.py`、`node scripts/verify_graffiti.cjs`、関連するCIブラウザー検証を通す。新規 ready は透過を必須とする。移行中の旧画像だけ `legacyPaper` を明示し、透過版への差し替え時に外す。

## デザインクレジット

グラフィティのアニメーション画面に `Designed by DJ Naoyaman` を表示する。画像へ焼き込まず、サイト側の固定クレジットとして全曲に適用する。

2026-10-17更新。ユーザー指示により40曲固定の公開単位を廃止。制作・公開は40曲などの固定件数で区切らず、生成サービス・実行環境・保存先の利用可能な範囲で、品質検証できる最大限の件数を進める。残り枠を取得できない場合は推測値を断定しない。各画像の完成ごとに保存し、上限や失敗を検知した場合は追加生成を止め、検証済みの成果をまとめて公開する。 既存の非透過画像を優先し、全掲載曲を透過画像へ更新する。画像適用数・透過完了数・公開数を分ける。

GRAFFITI ROOM の全ページ・全曲で `Designed by DJ Naoyaman` を常時表示する。共通テンプレートで生成し、トップページ・楽曲・アーティスト・特集等の全出力HTMLとPC/モバイルの表示を検証する。画像内の署名だけで代替しない。

## 全曲の配色とWall（2026-10-17）

全掲載曲で、グラフィティは収録アルバムの実際のジャケット配色を参照する。ブランド青・共通パレットで代用しない。未確認は未確認として制作前に照合し、参照先と編集上の近似を記録する。Wallはその配色の色相と明度から低彩度の壁色を決め、暗い作品には明るい壁、明るい作品には少し落ち着いた壁を合わせる。曲IDとseedから大判コンクリート・ブロック・漆喰の質感を固定し、再表示で不用意に変えない。地域の固定イメージは自動配色に使わない。全曲で文字の読みやすさと透明な余白を保つ。

最短で全曲の更新・公開を完了することを最優先とし、必要な品質検証を維持しつつ分担制作と既存の検証済み画像を活用する。

クレジットは `Designed by` の小さな活字と、`DJ Naoyaman`（`DJ NAOYAMAN`も可）の手書きグラフィティ署名を組み合わせる。署名は小さく、真の透過画像で全ページ共通に表示し、曲の作品と競合させない。代替テキストと全体のアクセシブル名は保持する。

## 曲のテンションと描画演出（2026-10-17）

build.pyとart_motion.pyが、掲載済みのmoods・deck・listening・essay先頭2段落から演出を決める。アーティスト・ジャンル・地域では決めない。音声やBPMを解析した表示にしない。具体的な強弱の手掛かりがない曲は中立のgrooveとし、曲IDとseedで速度と4種類の描画パターンを固定する。

- driftは柔らかな浮かび上がり、5.6〜7秒。
- grooveは帯・ブラシ・面・縦のストローク、3.2〜4.6秒。
- stompは重いブロックの打ち込み、2.2〜3秒。
- burstは中心から勢いよく広がる描画、1.2〜1.8秒。

手動調整はtracks.jsonのart.motionへmode・duration・variant・noteを記録する。画像と代替描画の両方に適用し、描画後は完成状態で静止する。動きを減らす設定では最初から完成状態を表示する。次回以降の追加曲にも自動適用する。対象曲数はtracks.jsonを正本とし、現在381曲。

## 楽曲画像内のサイト署名を入れない（2026-10-21）

今後生成・編集する楽曲グラフィティのビットマップには、DJ NAOYAMAN、DJ Naoyaman、CRATE DIGGIN'、CRATE DIGGIN’などのサイト名・制作者署名を入れない。プロンプトに明示し、公開前の画像目視でも混入がないことを確認する。曲名・アーティスト名・必要な版名と白い塗料、透過した余白は保持する。サイト外側のデザインクレジットと既定のalt表記はそのまま残す。ブランドアイコンおよびEDITOR自身の署名画像はこの楽曲画像ルールの対象外。

## 可視文字を基準にする表示サイズ（2026-10-24）

画像ファイルが正方形・高解像度でも、透明な余白が大きければ文字は小さく表示される。今後の新規・差替えタグアートは `artwork_display.py` の v1 基準で確認する。

- 計測対象はアルファ値8以上の全描画領域。曲名だけでなく、アーティスト名・版名・飛沫・垂れも含む。値1等の見えない符号化残滓を文字の大きさと誤認しない。
- 可視領域の上下左右に、それぞれ完成キャンバス寸法の7%（整数画素の丸め誤差のみ許容）の透明な安全余白を確保する。可視幅・高さは各約86%。正方形への強制配置や文字の引き伸ばしはしない。
- 記事の既存最大580×460px、ギャラリーや全画面の異なる枠に `contain` で収める。各枠の縦横比と絵の縦横比から決まる最大サイズの約86%を実インクが占める。縦長の作品を横長の作品と同じ幅へ無理に拡大しない。
- 元画像を保持し、別名の配信用WebPへキャンバスだけを正規化する。曲の文字・色・形・構成を再生成しない。全可視画素が同じ位置関係・同じRGBAで残ることを検査する。
- `python artwork_display.py normalize SOURCE.png assets/graffiti/ID-sized-v1.webp --report report.json` で正規化。出力はlossless WebP。`graffiti_artwork.json` の対象行に `displaySizing.version=1`、出力SHA256、visibleBox、元画像参照を記録する。
- `python artwork_display.py validate` と `python -m unittest discover -s scripts -p test_artwork_display.py` を実行。`build.py` も生成開始前に検査し、新規／画像変更の基準未達を拒否する。ビルドが画像を勝手に変換することはない。
- 旧作品は導入時の画像パス＋SHA256で限定的に保全する（`artwork_display_legacy.json`）。旧画像が変更された場合や新曲はこの免除を引き継がない。新規追加を通すために旧作品リストへ足さない。
- 白・暗い背景、小画面での可読性、文字の欠け、記事・ギャラリー・全画面のcontain後の見え方も確認する。自動数値検査だけで意匠確認を代替しない。

今回の対象は Urban Jazz／Spin Move／FREE.99。共通CSS・他曲の画像・曲データは変更せず、元の絵を保って余白のみ適正化する。


## 2026-10-24: タギングを主役にする
新規タグアートは手描き文字・線・筆勢を主役とし、コンセプトは字形、線の流れ、重なり、配色の範囲で表現する。3Dの立体装飾、文字の物体化、情景イラストやイラストロゴへ広げない。既存全画像の一括変換は行わず、新規・改訂時にこの基準を確認する。提供写真や通常の見出し文字は別用途として扱う。

## 2026-10-29: thirteen requested feature-name tags

The Beatnuts, Buckwild, Large Professor, Black Moon, Common, The Roots, Diamond D, 9th Wonder, RZA, Prince Paul, KRS-One, Mos Def and Da Beatminerz receive original black-and-white transparent name lettering in the existing `visual.nameOnly` component. This is feature-name artwork, not track jacket-derived art. No supplied portrait has been replaced or invented; photos have not yet been provided for these thirteen features and can be inserted later using the existing separate photo/name slots.

Each name was generated individually with the built-in image tool, decoded and visually checked for spelling, intact edges, readable white paint and transparency. The existing canvas-only normalizer preserves painted pixels and adds approximately seven-percent visible margins without rescaling. White pigment remains visually opaque (some generated white pixels use alpha 254, not exactly 255). Diamond D's punctuation-like extra stroke was removed using the image tool and rechecked. Original source images, per-image hashes and independent visual review are retained in the task's `recovery/features-13-20261029/art/` evidence folder. These name designs are original editorial lettering, not reproductions of official artist logos or endorsements.
