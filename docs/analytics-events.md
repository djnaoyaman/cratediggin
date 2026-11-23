# CRATE DIGGIN’ の行動計測

測定先は既存の `G-71ENPHWEJH`。今回、新しいイベント名やGoogleタグ/configは追加しません。

| 既存イベント | 利用する意味 |
| --- | --- |
| playback_start | 有効なYouTubeプレイヤーが実再生状態を返した時。ボタンの要求ではない |
| add_to_playlist / remove_from_playlist | MY CRATEの追加/削除がブラウザ保存まで成功した時 |
| reorder_playlist / restore_to_playlist | 並べ替え/取り消しを保存できた時 |
| share | clipboard成功、または今回追加したnative共有API成功 |

2026-11-23に保存失敗でも追加/削除として数えていた箇所を補正しました。一覧とアート画面の両方で保存結果を確認します。同じ選曲済み曲への追加は再送しません。共有は処理中の連打、キャンセル、失敗、取り外されたUIの古い完了を除外します。native成功はAPIの成功であり配送確認ではありません。

追加/補正箇所の送信ヘルパーはイベント別に許可したキーと固定値/公開IDだけを通し、send_toを固定、標準ga-disableを尊重します。MY CRATEの名前、自由入力、検索語、URLクエリ/フラグメントは送りません。page_locationはorigin+pathname、page_referrerは空。計測失敗は操作を中断しません。

既設のsample_playback_start、select_filter、select_listening_shelf、art_openは維持します。page_view/外部リンク/スクロールの同義イベントは追加しません。

生成元はsrc/app/navigation.js、playlist-ui.js、router.js。既存build_pipelineが共有バンドルへ組み込みます。局所確認で保存成功/失敗、native共有成功/キャンセル/連打、送信IDと許可パラメータを実行しました。公開後のGA受信とキーイベント指定は別工程です。
