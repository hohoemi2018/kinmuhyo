# ほほえみ勤務表（kinmuhyo）について

合同会社発達支援ほほえみカレッジが、保育園・児童発達支援・放課後等デイサービスの事業所に配っている勤務表アプリです。
公開先は GitHub Pages の https://hohoemi2018.github.io/kinmuhyo/ で、同じリンクを複数の事業所が使っています。

## ファイルの役割

- `index.html` … 公開中の勤務表アプリ（作り分けた結果。直接は編集しない）
- `_src/hohoemi-src.html` … 元ファイル。勤務表とタイムカードの両方のもとになる
- `_src/build.py` … 元ファイルから2つのアプリを作り分けるスクリプト
- タイムカードアプリは別リポジトリ `hohoemi2018/timecard` の `index.html`（公開先 https://hohoemi2018.github.io/timecard/）

`_src` と `.claude` は、先頭が `_` や `.` なので GitHub Pages では公開されません。

## 直すときの手順

1. `hohoemi2018/kinmuhyo` と `hohoemi2018/timecard` を、同じフォルダの中に並べて用意する（例：/home/claude/kinmuhyo と /home/claude/timecard）
2. `_src/hohoemi-src.html` を直す（中の `const APP='both';` は書きかえない。勤務表だけの部分は `HAS_ROSTER`、タイムカードだけの部分は `HAS_TC` で分けている）
3. kinmuhyo の一番上で `python3 _src/build.py` を実行する → `index.html` と `../timecard/index.html` が新しくなる
4. 動作を確かめる（両方のアプリを開いてエラーが出ないこと、以前のデータが読めること）
5. 2つのリポジトリそれぞれで commit して main に push する。2〜3分で公開される

## 大事な約束

- 入力データは各事業所のブラウザの localStorage に保存されている。キーは勤務表が `hohoemi-kinmuhyo-v1`、タイムカードが `hohoemi-timecard-v1`。このキーは変えない
- 新しい項目を足すときは、元ファイルの `normalize()` で「古いデータに無い項目は既定値で補う」ようにして、以前のデータがそのまま読めるようにする
- push すると、そのリンクを使うすべての事業所に一度に届く。必ず動作を確かめてから push する
- 画面の文章は、やさしい日本語で書く。画面の一番下の「合同会社発達支援ほほえみカレッジ作アプリ」は残す（印刷・PDFには出さない）
