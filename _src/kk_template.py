"""勤務形態一覧表（国の標準様式4）のひな形を作る。

使い方（kinmuhyo の一番上で）:
    python3 _src/kk_template.py

元ファイル _src/kk/hyojun-yoshiki4-r071128.xlsx（厚生労働省「標準様式４（勤務体制一覧表）」令和7年11月28日版）から、
児童発達支援・放課後等デイサービスなど3つのシートを、それぞれ「そのシート＋選択肢シート」だけのExcelにして
_src/kk/kk-jh.xlsx（児発・放デイ）・kk-js.xlsx（主として重症心身障害児）・kk-jc.xlsx（児童発達支援センター）に書き出す。
アプリはこのひな形に値を書きこんで、事業所に渡す。build.py が各リポジトリにコピーする。

することは：
- XML を直接けずる（openpyxl で保存し直すと見た目が変わるおそれがあるため）
- 共有の式（t="shared"）は、セルごとの式に開く（アプリが合計の式を値に置きかえても、ほかのセルの式がこわれないように）
- 式の計算結果（<v>）は消し、開いたときに計算し直すようにする（fullCalcOnLoad）
- 見本の値（職種・勤務形態・氏名の A〜E など）は消す。外部リンク・計算チェーン・プリンタ設定は外す
"""
import html
import os
import re
import zipfile

from openpyxl.formula.translate import Translator

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'kk', 'hyojun-yoshiki4-r071128.xlsx')
OUT = os.path.join(HERE, 'kk')

SERVICES = {
    'jh': ('xl/worksheets/sheet27.xml', '勤務形態一覧表（児童発達支援・放課後デイサービス）', '$A$1:$AN$76'),
    'js': ('xl/worksheets/sheet28.xml', '勤務形態一覧表（児童発達支援・主として重症心身障害児）', '$A$1:$AN$74'),
    'jc': ('xl/worksheets/sheet29.xml', '勤務形態一覧表（児童発達支援センター）', '$A$1:$AN$81'),
}
CHOICES = 'xl/worksheets/sheet34.xml'

CELL = re.compile(r'<c r="([A-Z]+)(\d+)"([^>]*?)(/>|>(.*?)</c>)', re.S)


def fix_sheet(xml, clear_sample=False, selected=True):
    # 1) 共有の式をセルごとに開く
    masters = {}
    for m in CELL.finditer(xml):
        body = m.group(5) or ''
        fm = re.search(r'<f t="shared" ref="[^"]*" si="(\d+)">(.*?)</f>', body, re.S)
        if fm:
            masters[fm.group(1)] = (m.group(1) + m.group(2), html.unescape(fm.group(2)))

    def cell(m):
        col, row, attrs, body = m.group(1), m.group(2), m.group(3), m.group(5)
        ref = col + row
        if body is None:
            return m.group(0)
        f = re.search(r'<f([^>]*)>(.*?)</f>|<f([^>]*)/>', body, re.S)
        if f:
            fa = f.group(1) if f.group(1) is not None else f.group(3)
            si = re.search(r'si="(\d+)"', fa or '')
            if 't="shared"' in (fa or '') and si:
                mref, mtext = masters[si.group(1)]
                text = mtext if mref == ref else Translator('=' + mtext, origin=mref).translate_formula(ref)[1:]
            else:
                text = html.unescape(f.group(2) or '')
            attrs = re.sub(r'\s+t="[^"]*"', '', attrs)
            return '<c r="%s"%s><f>%s</f></c>' % (ref, attrs, html.escape(text, quote=False))
        # 2) 見本の値を消す（職員の行の職種・勤務形態・資格・氏名）
        if clear_sample and 12 <= int(row) <= 31 and col in ('B', 'C', 'D', 'E'):
            attrs = re.sub(r'\s+t="[^"]*"', '', attrs)
            return '<c r="%s"%s/>' % (ref, attrs)
        return m.group(0)

    xml = CELL.sub(cell, xml)
    assert 't="shared"' not in xml
    # 3) プリンタ設定の参照を外す・選んでいるシート
    xml = re.sub(r'(<pageSetup[^>]*?)\s+r:id="[^"]*"', r'\1', xml)
    xml = re.sub(r'\s+tabSelected="1"', '', xml)
    if selected:
        xml = xml.replace('<sheetView ', '<sheetView tabSelected="1" ', 1)
    return xml


def names_from(workbook):
    keep = []
    for d in re.findall(r'<definedName [^>]*>[^<]*</definedName>', workbook):
        if '#REF' in d or 'localSheetId' in d or '[' in d:
            continue
        if '選択肢!' in d:
            keep.append(d)
    return keep


def build(code):
    part, name, area = SERVICES[code]
    z = zipfile.ZipFile(SRC)
    wb = z.read('xl/workbook.xml').decode('utf-8')
    names = ['<definedName name="_xlnm.Print_Area" localSheetId="0">\'%s\'!%s</definedName>' % (name, area)] + names_from(wb)
    workbook = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                '<workbookPr defaultThemeVersion="166925"/>'
                '<bookViews><workbookView xWindow="-110" yWindow="-110" windowWidth="19420" windowHeight="10300" activeTab="0"/></bookViews>'
                '<sheets><sheet name="%s" sheetId="1" r:id="rId1"/><sheet name="選択肢" sheetId="2" r:id="rId2"/></sheets>'
                '<definedNames>%s</definedNames><calcPr calcId="191028" fullCalcOnLoad="1"/></workbook>') % (name, ''.join(names))
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>'
            '<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            '<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>'
            '<Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sheetMetadata" Target="metadata.xml"/>'
            '</Relationships>')
    ss = 'application/vnd.openxmlformats-officedocument.spreadsheetml.'
    types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="xml" ContentType="application/xml"/>'
             '<Override PartName="/xl/workbook.xml" ContentType="' + ss + 'sheet.main+xml"/>'
             '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="' + ss + 'worksheet+xml"/>'
             '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="' + ss + 'worksheet+xml"/>'
             '<Override PartName="/xl/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
             '<Override PartName="/xl/styles.xml" ContentType="' + ss + 'styles+xml"/>'
             '<Override PartName="/xl/sharedStrings.xml" ContentType="' + ss + 'sharedStrings+xml"/>'
             '<Override PartName="/xl/metadata.xml" ContentType="' + ss + 'sheetMetadata+xml"/>'
             '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
             '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
             '</Types>')
    app = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
           'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Microsoft Excel</Application></Properties>')
    out = os.path.join(OUT, 'kk-%s.xlsx' % code)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as o:
        o.writestr('[Content_Types].xml', types)
        o.writestr('_rels/.rels', z.read('_rels/.rels'))
        o.writestr('docProps/core.xml', z.read('docProps/core.xml'))
        o.writestr('docProps/app.xml', app)
        o.writestr('xl/workbook.xml', workbook)
        o.writestr('xl/_rels/workbook.xml.rels', rels)
        o.writestr('xl/worksheets/sheet1.xml', fix_sheet(z.read(part).decode('utf-8'), clear_sample=True, selected=True))
        o.writestr('xl/worksheets/sheet2.xml', fix_sheet(z.read(CHOICES).decode('utf-8'), selected=False))
        for p in ('xl/theme/theme1.xml', 'xl/styles.xml', 'xl/sharedStrings.xml', 'xl/metadata.xml'):
            o.writestr(p, z.read(p))
    print(code, '->', out, os.path.getsize(out))


if __name__ == '__main__':
    for c in SERVICES:
        build(c)
