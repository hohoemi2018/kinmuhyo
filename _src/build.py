"""ほほえみ勤務表・ほほえみタイムカードを、1つの元ファイルから作り分ける。

使い方（このリポジトリの一番上で）:
    python3 _src/build.py                 # index.html（勤務表）と ../timecard/index.html（タイムカード）を作る
    python3 _src/build.py --timecard PATH # タイムカードの出力先を指定する

元ファイル _src/hohoemi-src.html の中の const APP='both'; を
'roster'（勤務表だけ）/'timecard'（タイムカードだけ）に置きかえて、
完全なHTML文書として書き出す。
"""
import argparse
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(HERE, 'hohoemi-src.html')

HEAD = ('<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
        'body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n')


def variant(src, app, title):
    assert src.count("const APP='both';") == 1, '元ファイルに const APP=\'both\'; が1つだけあるはずです'
    return (src.replace("const APP='both';", "const APP='%s';" % app)
               .replace('<title>ほほえみ勤務表</title>', '<title>%s</title>' % title))


def full(fragment):
    i = fragment.index('<div class="app" id="app">')
    return HEAD + fragment[:i] + '</head>\n<body>\n' + fragment[i:] + '\n</body>\n</html>\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kinmuhyo', default=os.path.join(REPO, 'index.html'))
    ap.add_argument('--timecard', default=os.path.join(os.path.dirname(REPO), 'timecard', 'index.html'))
    a = ap.parse_args()
    src = open(SRC, encoding='utf-8').read()
    for app, title, out in (('roster', 'ほほえみ勤務表', a.kinmuhyo), ('timecard', 'ほほえみタイムカード', a.timecard)):
        if not os.path.isdir(os.path.dirname(out)):
            print('スキップ（フォルダがありません）:', out)
            continue
        with open(out, 'w', encoding='utf-8') as f:
            f.write(full(variant(src, app, title)))
        print(app, '->', out)


if __name__ == '__main__':
    main()
