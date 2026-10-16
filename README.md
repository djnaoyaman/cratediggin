# Crate Diggin’

A Guide to Sampled Mind & Vintage Grooves

選曲・編集・文責 DJ Naoyaman。

公開先 https://djnaoyaman.github.io/cratediggin/

## 制作

`tracks.json` が楽曲データ、`releases.json` がバージョンと主要機能の履歴です。

```sh
python -m pip install Pillow
python build.py
```

静的サイトを `dist/` に生成します。mainへアップロードするたびGitHub Actionsが検証・再生成・GitHub Pagesへの公開を行います。GitHub PagesのSourceはGitHub Actionsを選択してください。

## バージョン

大きな機能変更は前の数字を増やし、後ろを0に戻します。細かな修正は後ろだけ増やします。履歴は大きな機能変更だけ、Aboutの末尾に日本時間で表示します。導入前の履歴は実際の公開記録から遡って採番しています。

```sh
python version.py --major --title "機能の名前" --description "変更内容"
python version.py --minor
```

曲追加の詳細は `ADDING_TRACKS.md` を参照。音源・グラフィティの利用や配信可否は各権利者と配信サービスの条件に従います。

MY CRATEの選曲・名前・曲順はブラウザのlocalStorageに保存します。左スワイプで外す、右スワイプで選曲。•••ボタンからも操作でき、選曲の削除は取り消せます。保存は端末・ブラウザ単位です。

## 品質監査と公開前の確認

`python scripts/audit_catalog.py` はカタログ全曲の楽曲ID、YouTube IDとURLの整合性、出典、文章の必須項目、未確認のレーベル・初出年を監査します。結果は `audit-reports/catalog-audit.csv` と `audit-reports/summary.json` に出力します。

`python scripts/audit_catalog.py --online` はYouTube oEmbedの動画タイトル・投稿者を照合する追加調査です。タイトルの一致は正しい録音・バージョン・再生可能性を証明しません。疑義のある曲は実際の音源と盤面を人が照合してください。

公開URLと既存の楽曲IDを維持します。フロントエンドの編集元は `src/`、共通HTMLは `templates/index.html` です。`dist/` はビルド生成物のため直接編集しません。

## 聴きどころの選曲棚

`listening_shelves.json` は「ループの妙／ドラムの手触り／ベースのうねり／声とライム／スクラッチの技／曲の展開」の6つの聴き方と、解説を個別に読んで選んだ楽曲を管理します。ジャンルやアーティスト名から一括分類しません。各タグには `tracks.json` または `editorial_deepdives.json` の該当箇所と短い根拠を持たせ、ビルド時に一致を検証します。複数の棚への所属が可能です。未分類曲も「すべて」および検索で見つけられます。

棚の件数は検索・補助条件を反映し、0件の棚は選択不可になります。地域は折りたたみ式の補助フィルターです。旧 `editorialCrates` は過去データとして保存しますが、現在の棚判定には使いません。旧棚のURLは全曲に戻し、東西海岸の旧URLは地域条件として維持します。

検証: `node scripts/verify_listening_shelves.js`。ブラウザ検証は `node scripts/verify_listening_shelves_browser.js`（PlaywrightとChromiumが必要。`dist` を `/cratediggin` 配下でローカル配信し、`TEST_URL` でURLを指定。CIでも公開前に実行）。

## ソース構成と再生成

- `src/app/` — 共通状態、MY CRATE、再生、一覧、楽曲記事、特集、画面遷移を分けたJavaScript。`order.json` の順で単一のプライベートスコープに連結します。
- `src/assets/` — CSS、アート、フィルター、プレイリスト、年表のソース。
- `templates/index.html` — 記事本文を含まない共通HTML。
- `frontend.py` — ソースの連結と明示的なデータ差し込み。ビルドはソースを書き換えません。
- `dist/` と `audit-reports/` — Git管理しない生成物。`dist/` がなくても `python build.py` で再生成できます。

Pythonのテキスト入出力はUTF-8を明示しています。`node scripts/verify_pagination_browser.cjs` は専用のローカルサーバーを起動し、一覧への戻り位置、検索、再読み込み、MY CRATEの並べ替え・削除・取り消しをPC・スマートフォン幅で検証します。CIでも公開前に実行します。


## SEO・SNS・AI検索向けの公開情報

`discovery.py` が、静的HTMLと画面移動時に使うメタ情報を同じデータから生成します。`metadata.js` は軽量なページ索引、`metadata/*.json` は各ページの構造化データです。曲・特集・アーティスト・ガイド・編者紹介は実ページURLを持ち、通常の移動はHistory APIで再生状態を保持します。旧 `#/song/...` 等のURLは実URLへ正規化します。

`artist_entities.json` は個人・グループの明示的な分類です。参加名義などを確認できない場合は `null` にし、メンバー欄の区切り文字から推測しません。新しいアーティストを追加する際は、この索引にも追加してください。

記事公開日は元データに存在する値だけを出力します。`revision_dates.py` は本文データと深掘り記事のGit履歴を比較し、確認できる改訂の日時だけを出力します。履歴が不足・破損している箇所や未コミットの変更に、ビルド日時を記事更新日として付けません。CIは完全なGit履歴を取得します。`article-revisions.json` は改訂根拠のコミットを記録します。

Markdownには正規URL、著者、確認できた日付、確認継続中の項目を添えます。`llms.txt` は利用するサービスへの補助情報であり、Googleの検索順位やAI回答での引用を保証するものではありません。レーベル・初出年・録音の照合待ちは、技術的な整備によって確認済みにはなりません。

クローラーが参照するrobots.txtは `https://djnaoyaman.github.io/robots.txt` です。別リポジトリ `djnaoyaman/djnaoyaman.github.io` で既存の制限を維持し、Crate Digginのサイトマップを案内します。Search ConsoleやBing Webmaster Toolsの登録・インデックス状況は各管理画面で確認してください。

## 利用行動と広告効果の計測

GA4に以下のイベントを送ります。ページ表示は実URLとタイトルで送信し、初回流入のUTMや広告クリックIDは一覧の条件変更でも保持します。計測用の固定値と公開楽曲IDだけを独自イベントに含め、プレイリスト名や入力した検索語は送信しません。

| イベント | 発火条件 | 主なパラメータ |
|---|---|---|
| `playback_start` | YouTubeが実際に楽曲の再生開始を通知したとき。重複する再生状態通知は除外 | `song_id`, `content_type` |
| `add_to_playlist` | MY CRATEへの追加 | `song_id` |
| `remove_from_playlist` | MY CRATEからの削除 | `song_id` |
| `restore_to_playlist` | 削除の取り消し | `song_id` |
| `reorder_playlist` | 曲順変更の成功 | `song_id`, `direction` |
| `share` | 正規URLのコピー、または端末の共有操作の成功 | `method`, `content_type`, `item_id` |

手動のページ表示イベントと二重計測にならないよう、GA4の拡張計測で履歴変更による自動ページ表示の設定も確認してください。GA4管理画面のキーイベント指定、カスタムディメンション登録、Google Adsとの連携はアカウント側の設定です。ソースのイベント追加だけでは広告コンバージョンの設定完了にはなりません。ブラウザテストでは外部の計測スクリプトを止め、イベントのキューだけを検証します。

追加検証: `python scripts/verify_discovery.py`、`python scripts/test_revision_dates.py`、`node scripts/verify_discovery_browser.cjs`。静的HTML、OGP、canonical、画像、実URLの内部リンク、構造化データと改訂根拠、画面移動・共有・計測・JavaScript無効時の本文を検証します。
