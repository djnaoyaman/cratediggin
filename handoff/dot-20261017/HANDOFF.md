# CRATE DIGGIN’ ドットくん引継書

2026年10月17日作成。ユーザー指示により、このチャットの画像制作・実装・公開を停止。引き継ぎ保存のみ実施した。ドットくんへの直接送信・受領確認は未実施。

## 保存先と基準
- リポジトリ https://github.com/djnaoyaman/cratediggin
- 本番 https://djnaoyaman.github.io/cratediggin/
- 引継専用ブランチ handoff/dot-20261017 。本書、unpublished-assets.json、unpublished/ 以下に既知の未公開画像27点を保存。mainへの適用・PR作成・デプロイは行わない。
- 確認したmain 05a8ecf94db85092ffa341f0053ae24844225bb2 。PR43の曲ごとの演出変更まで取り込み済み。main対応のPages実行39012537957はsuccess。別のPages成功実行39013127724も存在し、そちらのheadは042c6ed576c56f91ed4e025a19b941b2c64934fa。公開実体とmainの完全一致は今回再検証していない。
- 現在のmanifestは381曲、ready画像56曲、そのうちtransparent指定53曲、旧非透過3曲。今回は既存manifest集計であり全画像の再デコード検査ではない。元の371曲から追加があるため残数358をそのまま使わず、現在の381曲で再計算する。透明化未完了は指定上328曲。
- 初回40曲はPR40でmainへ反映済み。古いローカルの「未デプロイ」という記録よりmainを優先する。

## 未公開成果と欠損
- unpublished-assets.json にbatch80の26点とbatch120の1点のGit blob SHA、保存パス、現manifest状態を記録。ファイル名のIDは旧作業記録由来であり、特にPublic EnemyのShut Em DownとCraig Mackは現在の正式IDと照合する。
- 27点は保存用素材であり公開済み・最新品質の再検証済みとは数えない。現在mainに同じ曲があれば重複制作せず比較する。
- Main Source「Just Hangin’ Out」とBrand Nubian「All For One」は配色修正待ち。現在の保存画像をそのままreadyにしない。
- 前者はBreaking Atomsを参照し #d641a8 #53c6d8 #f1e58a #30243f 。参照 https://townsquare.media/site/812/files/2017/07/breaking-atoms-cover.jpg
- 後者はOne for Allを参照し #be483b #e2c64a #498866 #66516f 。参照 https://www.plexusrecords.com/upload/image/one-for-all-p-image-85096-grande.jpg
- 旧batch80作業は34点レビュー済みという中間報告だったが、うち8点はアップロードSHA未記録。Jeru「Come Clean」「Ya Playin’ Yaself」、Nas「It Ain’t Hard to Tell」「N.Y. State of Mind」、Public Enemy「911 Is a Joke」、Biggie「Juicy」、Wu-Tang「C.R.E.A.M.」、De La Soul「Stakes Is High」。元ファイルの現存を確認できず、完成・保存済みには数えない。画像履歴等から復旧できなければ再制作。
- 残りbatch80の6点は未完了または背景不良で却下。De La Soul「Breakadawn」は実ジャケットのターコイズ・赤・黄へ修正中だった。batch120の2点目は中間集計のみで曲名/SHA不明、計上しない。
- 旧保存先 /workspace/scratch/09959dbb4dee/crate-release は現在存在しない。そこにあったbatch80-assets-*.json等の完全なレビュー記録・原画も未回収。
- 現存する旧ローカル /workspace/scratch/c2acef5da05d/crate-publish は参考スナップショット。Git管理先が消失してgit statusが失敗し、カタログも古い。ここをそのままmainへ上書きしない。fresh cloneを使う。

## ブランチと保存履歴
- work/graffiti-next40 はPR40でマージ済み。feature/graffiti-batches-40 はPR37、feature/album-colored-walls はPR38、feature/dj-naoyaman-marker-tag はPR39でマージ済み。
- feature/graffiti-batches-30 は旧30曲計画。work/graffiti-next40 とともにユーザーが整理を希望したが、削除は未完了。差分・未回収ファイルを確認してから整理する。
- 旧checkpoint 6bfc4203603a7f51f024a7aef8fdec0bda3d690a はfirst40の27画像とbatch80の8画像、research/batch40-progress.json と research/batch80-progress.json を保持していた。後者8件は後続26件の完全な記録ではない。
- 保存試行commit f76e77cc3548f8e8089fba8f1b0ba87d9581c401 は参照更新できなかった孤立commit。PR40に含まれたfirst40のため再適用不要。これを正式保存先としない。
- GitHubへのtracks.jsonアップロードでuser rejected MCP tool callの応答があった。拒否された同等操作を別経路で回避しない。他チャットで既にPR40公開済みなので、この旧アップロードは再試行不要。
- HTTPS git pushは認証情報がなく失敗した。ブランチ削除ツールも未提供だった。削除完了を報告しない。

## 必須制作・実装ルール
- 承認済みMass Appeal品質の複雑なオリジナルグラフィティを全曲で維持。曲名・アーティスト名・必要なバージョン表記を正確にし、欠けと小画面での読め方を確認。
- 全曲の配色は収録アルバムの実ジャケットに合わせる。共通ブランド青は禁止。既存paletteも鵜呑みにせず参照を確認し、paletteSourceと目視近似のpaletteNoteを記録。
- 真のアルファ透過、白い塗料の不透明部分を保持。紙・壁・チェッカー・背景の霞を画像へ焼き込まない。全デコードとalpha最小値0、文字・縁・配色の目視確認が必要。
- Wallはサイト側。作品配色から低彩度の色を導出し、曲ID/seedで大判コンクリート・ブロック・漆喰を固定的に変化させる。地域イメージによる自動配色は禁止。
- altは自動で「曲名 — アーティスト名｜CRATE DIGGIN｜DJ Naoyaman」。
- 全GRAFFITI ROOMで Designed by DJ Naoyaman の固定クレジットを維持。Designed byは小さく、DJ NAOYAMANは小さなサインペンのタギング画像。src/assets/dj-naoyaman-signature-v2.webpが承認済みの角張ったマーカー署名。全生成HTMLの静的検証とPC/モバイルの表示検証を維持。
- 古い画像の一瞬表示を再発させない。曲切替直後は現在曲の壁と画像のみ。画像未ロード・失敗時に前曲や旧canvasを出さない。art.js/releases.jsのバージョン付きURLも保持。
- tracks.json と graffiti_artwork.json を整合させる。sourceを編集してbuildし、distだけを直さない。
- AGENTS.md、ARTWORK_NOTES.md、ADDING_TRACKS.md、research/graffiti-batch-plan.jsonの現mainを確認。40曲単位、最終端数は残数。旧30/50曲の指示より40曲を優先。
- Featuresは後世への影響が大きく3曲以上収録のアーティスト、裏付けのある同一名義はまとめる。年表にサンプル曲を戻さず、SUBURBIA CLASSICAのリンクを保持。

## ドットくんの再開手順
1. 最新mainと進行中PRを確認してfresh clone。ユーザーによる別チャットの変更を上書きしない。
2. 引継ブランチの27画像とmainの既存画像を照合し、再利用できる素材を先に使う。足りない配色・参照・レビュー記録を補完。
3. 旧非透過3曲を優先し、未制作曲を40曲単位で進める。各画像を検証後すぐ参照付きcommitで保存し、blobのみで放置しない。
4. python build.py、node scripts/verify_graffiti.cjs、既存Actions、全ページクレジットとPC/モバイルを必要範囲で検証。PRマージとPages成功を確認して初めて公開完了と数える。
5. 適用曲数、真の透過検証完了数、実公開数を分けて報告する。

## 停止状態
このチャットの6制作ワーカーはすべてshutdownを確認。継続タスク「CRATE DIGGIN’ 全曲アート更新」は無効を確認・維持した。このチャットから再開・新規生成・実装・公開は行わない。別チャットやドットくんの稼働状態は管理していない。
