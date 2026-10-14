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
