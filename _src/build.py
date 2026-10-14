"""ほほえみ勤務表・ほほえみタイムカード・合わせたアプリを、1つの元ファイルから作り分ける。

使い方（このリポジトリの一番上で）:
    python3 _src/build.py                 # 3つとも作る
        index.html                        … 勤務表だけ（このリポジトリ）
        ../timecard/index.html            … タイムカードだけ
        ../kinmuhyo-timecard/index.html   … 勤務表とタイムカードを合わせたアプリ
    python3 _src/build.py --both PATH     # 合わせたアプリの出力先を指定する（--kinmuhyo / --timecard も同じ）

元ファイル _src/hohoemi-src.html の中の const APP='both'; を
'roster'（勤務表だけ）/'timecard'（タイムカードだけ）/'both'（合わせたアプリ）に置きかえて、
完全なHTML文書として書き出す。出力先のフォルダがないものはスキップする。

あわせて、iPad・タブレットの「ホーム画面に追加」のための manifest.webmanifest と
アイコン（_src/icons/<アプリ>-*.png → icon-180.png など）を、それぞれの出力先に書き出す。
"""
import argparse
import json
import os
import shutil

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


# ホーム画面に追加したときの名前（短い名前）と、アプリの説明
HOME = {
    'roster': ('ほほえみ勤務表', '保育園・児童発達支援・放課後等デイサービスのための勤務表のアプリです。'),
    'timecard': ('タイムカード', '保育園・児童発達支援・放課後等デイサービスのためのタイムカードのアプリです。'),
    'both': ('勤務表・タイムカード', '保育園・児童発達支援・放課後等デイサービスのための勤務表とタイムカードのアプリです。'),
}
ICONS = (('180', 'icon-180.png'), ('192', 'icon-192.png'), ('512', 'icon-512.png'), ('maskable-512', 'icon-maskable-512.png'))


def home_head(app):
    short = HOME[app][0]
    return ('<link rel="manifest" href="manifest.webmanifest">\n'
            '<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">\n'
            '<link rel="apple-touch-icon" href="icon-180.png">\n'
            '<meta name="apple-mobile-web-app-capable" content="yes">\n'
            '<meta name="mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-title" content="%s">\n'
            '<meta name="theme-color" media="(prefers-color-scheme: light)" content="#FFF3E8">\n'
            '<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#2A201B">\n' % short)


def manifest(app, title):
    short, desc = HOME[app]
    return json.dumps({
        'name': title, 'short_name': short, 'description': desc, 'lang': 'ja',
        'id': './', 'start_url': './', 'scope': './', 'display': 'standalone',
        'background_color': '#FFF3E8', 'theme_color': '#FFF3E8',
        'icons': [
            {'src': 'icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
            {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
            {'src': 'icon-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
        ],
    }, ensure_ascii=False, indent=2) + '\n'


def full(fragment, app='both'):
    i = fragment.index('<div class="app" id="app">')
    return HEAD + home_head(app) + fragment[:i] + '</head>\n<body>\n' + fragment[i:] + '\n</body>\n</html>\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kinmuhyo', default=os.path.join(REPO, 'index.html'))
    ap.add_argument('--timecard', default=os.path.join(os.path.dirname(REPO), 'timecard', 'index.html'))
    ap.add_argument('--both', default=os.path.join(os.path.dirname(REPO), 'kinmuhyo-timecard', 'index.html'))
    a = ap.parse_args()
    src = open(SRC, encoding='utf-8').read()
    for app, title, out in (('roster', 'ほほえみ勤務表', a.kinmuhyo), ('timecard', 'ほほえみタイムカード', a.timecard),
                            ('both', 'ほほえみ勤務表・タイムカード', a.both)):
        if not os.path.isdir(os.path.dirname(out)):
            print('スキップ（フォルダがありません）:', out)
            continue
        with open(out, 'w', encoding='utf-8') as f:
            f.write(full(variant(src, app, title), app))
        d = os.path.dirname(out)
        with open(os.path.join(d, 'manifest.webmanifest'), 'w', encoding='utf-8') as f:
            f.write(manifest(app, title))
        for suf, name in ICONS:
            shutil.copyfile(os.path.join(HERE, 'icons', '%s-%s.png' % (app, suf)), os.path.join(d, name))
        print(app, '->', out)


if __name__ == '__main__':
    main()
