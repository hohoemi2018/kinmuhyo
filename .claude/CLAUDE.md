# ほほえみ勤務表（kinmuhyo）について

合同会社発達支援ほほえみカレッジが、保育園・児童発達支援・放課後等デイサービスの事業所に配っている勤務表アプリです。
公開先は GitHub Pages の https://hohoemi2018.github.io/kinmuhyo/ で、同じリンクを複数の事業所が使っています。

## ファイルの役割

- `index.html` … 公開中の勤務表アプリ（作り分けた結果。直接は編集しない）
- `_src/hohoemi-src.html` … 元ファイル。勤務表とタイムカードの両方のもとになる
- `_src/build.py` … 元ファイルから3つのアプリを作り分けるスクリプト
- タイムカードアプリは別リポジトリ `hohoemi2018/timecard` の `index.html`（公開先 https://hohoemi2018.github.io/timecard/）
- 勤務表とタイムカードを合わせたアプリは別リポジトリ `hohoemi2018/kinmuhyo-timecard` の `index.html`（公開先 https://hohoemi2018.github.io/kinmuhyo-timecard/）

`_src` と `.claude` は、先頭が `_` や `.` なので GitHub Pages では公開されません。

## 直すときの手順

1. `hohoemi2018/kinmuhyo`・`hohoemi2018/timecard`・`hohoemi2018/kinmuhyo-timecard` を、同じフォルダの中に並べて用意する（例：/home/claude/kinmuhyo、/home/claude/timecard、/home/claude/kinmuhyo-timecard）
2. `_src/hohoemi-src.html` を直す（中の `const APP='both';` は書きかえない。勤務表の部分は `HAS_ROSTER`、タイムカードの部分は `HAS_TC` で分けている。合わせたアプリは両方とも true。合わせたアプリだけの部分は `APP==='both'`）
3. kinmuhyo の一番上で `python3 _src/build.py` を実行する → `index.html`・`../timecard/index.html`・`../kinmuhyo-timecard/index.html` が新しくなる
4. 動作を確かめる（3つのアプリを開いてエラーが出ないこと、以前のデータが読めること）
5. 3つのリポジトリそれぞれで commit して main に push する。2〜3分で公開される

## 大事な約束

- 入力データは各事業所のブラウザの localStorage に保存されている。キーは勤務表が `hohoemi-kinmuhyo-v1`、タイムカードが `hohoemi-timecard-v1`、合わせたアプリが `hohoemi-kinmuhyo-tc-v1`。このキーは変えない
- 合わせたアプリの「これまでのデータを取りこむ」は、同じ端末の `hohoemi-kinmuhyo-v1` と `hohoemi-timecard-v1` を読むだけで、書きかえない（3つとも hohoemi2018.github.io にあるので読める）
- 希望休の値は W＝希望休、P＝有給（1日）、H＝有給（半日。勤務表では出勤の日として組む）。合わせたアプリでは、勤務表の P・H がタイムカードの有給になる（公開前は管理者の個人の記録にだけ出し、合計・集計には公開後に入れる）
- 新しい項目を足すときは、元ファイルの `normalize()` で「古いデータに無い項目は既定値で補う」ようにして、以前のデータがそのまま読めるようにする
- 勤務の種類は `S.shiftIds`（ならび順）と `S.shifts[id]`（name・ab＝表の文字・abAuto・col＝色0〜7・start・end・wk・we・del）。はじめの3つは id が E・N・L、あとから足した勤務は id が x で始まる（8つまで）。勤務表に入っている勤務を消すときは `del:true` で残す（前の月の表を出すため）。「遅番の次の日に早番を入れない」は、名前に「早」「遅」がつく勤務で決める。既定の3つのときは、自動作成の結果が以前の版と同じになるようにしてある（変えたら、同じ乱数で前の版と結果をくらべて確かめる）
- 職員の勤務時間は `s.hrs`（時間1）と `s.hrs.alt`（時間2〜5。dows＝使う曜日）。勤務表のマスで日ごとに選び直した時間は、その月の表の `hb[職員id][日]`（0＝時間1）
- ご利用の登録：購入・特典の事業所だけが使える。利用リンク `…/#lic=<トークン>` は、さとよさんの発行ページ（claude.ai の非公開アーティファクト「ほほえみ利用リンク発行」）で、さとよさんだけが持つ秘密のかぎ（ECDSA P-256）で署名して作る。アプリには公開かぎ `LIC_PUB` だけを入れる（かぎを変えるときは、古い公開かぎも `LIC_PUB` に残して並べる）。登録は localStorage の `hohoemi-license-v1`（3つのアプリで共有。トークンの中の a＝使えるアプリ k/t/b、g＝特典、x＝期限）。この仕組みを入れる前からデータがある端末は `hohoemi-legacy-v1` の印で、登録なしでそのまま使える（データに `lv` がない＝前の版のデータ）。期限切れは見る・控え・PDFだけ（`VIEW_ACTS`）。これらのキーも変えない。テストで新しい端末を開くときは `hohoemi-legacy-v1` を入れておくか、テスト用のトークンを使う
- データの控え：パスワードをかけるかどうかを事業所が選ぶ。パスワードつきの控えは `HOHOEMI-ENC2:`（データのかぎ DK を ①パスワード ②控えの予備のコード `S.bkrc`（事業所ごとに1つ。パスワードなしの控えには入れない） ③ほほえみカレッジ（`BK_ESCROW`＝`LIC_PUB[0]` への ECDH）の3通りで包む）。③は「問い合わせの文字」（HQ1.）を発行ページに貼ると解除コード（HK1-…）ができる。控えの中身はさとよさんに届かない。前の形 `HOHOEMI-ENC1:`（パスワードだけ）とパスワードなし（JSON）も戻せるようにしておく
- push すると、そのリンクを使うすべての事業所に一度に届く。必ず動作を確かめてから push する
- 画面の文章は、やさしい日本語で書く。画面の一番下の「合同会社発達支援ほほえみカレッジ作アプリ」は残す（印刷・PDFには出さない）
