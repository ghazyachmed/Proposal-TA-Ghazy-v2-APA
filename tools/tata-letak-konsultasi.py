#!/usr/bin/env python3
"""Rapikan tata letak DOCX konsultasi supaya nyaman dibaca.

- Judul TA & identitas penulis langsung di atas I.1, tanpa cover & daftar isi.
  Judul, nama, NIM, & prodi dibaca dari blok IDENTITAS DOKUMEN di ProposalTA.tex
- Halaman A4 dengan margin ta-sti.cls (kiri 4 cm, kanan/atas/bawah 3 cm) & nomor halaman di kaki
- Gaya teks mengikuti PDF LaTeX: judul bagian hitam tebal 12pt, spasi 1,5, jarak paragraf 12pt
- Tabel bergaris, isi 10pt spasi tunggal, baris judul tebal berlatar abu-abu, judul tabel di tengah

    python3 tools/tata-letak-konsultasi.py docs/Konsultasi-Latar-Belakang.docx
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
DOCX = Path(sys.argv[1])

# A4, margin ta-sti.cls: kiri 4 cm, kanan/atas/bawah 3 cm (1 cm = 567 twip)
SECT = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdKakiHal" />'
        '<w:pgSz w:w="11906" w:h="16838" />'
        '<w:pgMar w:top="1701" w:right="1701" w:bottom="1701" w:left="2268" w:header="709" w:footer="709" w:gutter="0" />'
        '<w:pgNumType w:start="1" /></w:sectPr>')

GAYA = {
    "Heading1": ('<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1" /><w:basedOn w:val="Normal" />'
                 '<w:next w:val="BodyText" /><w:uiPriority w:val="9" /><w:qFormat /><w:pPr><w:keepNext /><w:keepLines />'
                 '<w:spacing w:before="240" w:after="120" w:line="360" w:lineRule="auto" /><w:outlineLvl w:val="0" /></w:pPr>'
                 '<w:rPr><w:b /><w:bCs /><w:color w:val="000000" /><w:sz w:val="24" /><w:szCs w:val="24" /></w:rPr></w:style>'),
    "BodyText": ('<w:style w:type="paragraph" w:styleId="BodyText"><w:name w:val="Body Text" /><w:basedOn w:val="Normal" />'
                 '<w:link w:val="BodyTextChar" /><w:qFormat /><w:pPr><w:spacing w:before="0" w:after="240" w:line="360" w:lineRule="auto" />'
                 '<w:jc w:val="both" /></w:pPr></w:style>'),
    # Compact dipakai pandoc untuk butir daftar bernomor
    "Compact": ('<w:style w:type="paragraph" w:customStyle="1" w:styleId="Compact"><w:name w:val="Compact" /><w:basedOn w:val="BodyText" />'
                '<w:qFormat /><w:pPr><w:spacing w:before="0" w:after="60" w:line="360" w:lineRule="auto" /></w:pPr></w:style>'),
    "IsiTabel": ('<w:style w:type="paragraph" w:customStyle="1" w:styleId="IsiTabel"><w:name w:val="Isi Tabel" /><w:basedOn w:val="Normal" />'
                 '<w:qFormat /><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto" /><w:jc w:val="left" /></w:pPr>'
                 '<w:rPr><w:sz w:val="20" /><w:szCs w:val="20" /></w:rPr></w:style>'),
}

GARIS = ''.join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="000000" />'
                for s in ("top", "left", "bottom", "right", "insideH", "insideV"))


def identitas():
    nilai = {}
    for baris in (ROOT / "ProposalTA.tex").read_text(encoding="utf-8").splitlines():
        if baris.lstrip().startswith("%"):
            continue
        m = re.match(r"\s*\\newcommand\{\\(judulta|namapenulis|nimpenulis|prodita)\}\{(.*?)\}\s*(%.*)?$", baris)
        if m:
            nilai[m.group(1)] = m.group(2)
    for k in ("judulta", "namapenulis", "nimpenulis", "prodita"):
        if k not in nilai:
            sys.exit(f"Identitas \\{k} tidak ditemukan di ProposalTA.tex")
    return nilai


def para(teks, ukuran, tebal=False, sesudah=0, garis_bawah=False):
    bdr = '<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="8" w:color="000000" /></w:pBdr>' if garis_bawah else ""
    rpr = ("<w:b /><w:bCs />" if tebal else "") + f'<w:sz w:val="{ukuran}" /><w:szCs w:val="{ukuran}" />'
    return (f'<w:p><w:pPr>{bdr}<w:spacing w:before="0" w:after="{sesudah}" w:line="240" w:lineRule="auto" /><w:jc w:val="center" /></w:pPr>'
            f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(teks)}</w:t></w:r></w:p>')


def kepala(idn):
    return (para(idn["judulta"], 28, True, 160)
            + para(f'{idn["namapenulis"]} ({idn["nimpenulis"]})', 22)
            + para(f'Program Studi {idn["prodita"]}, Institut Teknologi Bandung', 22, sesudah=360, garis_bawah=True))


def rapikan_tabel(tbl):
    tbl = tbl.replace('<w:pStyle w:val="Compact" />', '<w:pStyle w:val="IsiTabel" />')
    tbl = tbl.replace("<w:tblLayout", f"<w:tblBorders>{GARIS}</w:tblBorders><w:tblLayout", 1)
    tbl = tbl.replace("<w:tblLook", '<w:tblCellMar><w:top w:w="40" w:type="dxa" /><w:left w:w="80" w:type="dxa" />'
                      '<w:bottom w:w="40" w:type="dxa" /><w:right w:w="80" w:type="dxa" /></w:tblCellMar><w:tblLook', 1)
    baris = re.findall(r"<w:tr>.*?</w:tr>", tbl, re.S)
    baru = []
    for i, tr in enumerate(baris):
        if i == 0:
            # Baris judul kolom: tebal & berlatar abu-abu muda
            tr = tr.replace("<w:tcPr />", '<w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="EDEDED" /></w:tcPr>')
            tr = tr.replace("<w:r><w:rPr>", "<w:r><w:rPr><w:b />").replace("<w:r><w:t", "<w:r><w:rPr><w:b /></w:rPr><w:t")
        else:
            # Sel pertama kosong = lanjutan sel di atasnya, digabung vertikal seperti \cline di LaTeX
            sel = re.search(r"<w:tc>.*?</w:tc>", tr, re.S).group(0)
            if not re.sub(r"<[^>]+>", "", sel).strip():
                tr = tr.replace("<w:tcPr />", '<w:tcPr><w:vMerge /></w:tcPr>', 1)
                if not re.search(r"<w:vMerge", baru[-1].split("</w:tc>")[0]):
                    baru[-1] = baru[-1].replace("<w:tcPr />", '<w:tcPr><w:vMerge w:val="restart" /></w:tcPr>', 1)
        baru.append(tr)
    for lama, b in zip(baris, baru):
        tbl = tbl.replace(lama, b, 1)
    return tbl


def main():
    idn = identitas()
    with zipfile.ZipFile(DOCX) as z:
        isi = {n: z.read(n) for n in z.namelist()}

    gaya = isi["word/styles.xml"].decode("utf-8")
    for sid, xml in GAYA.items():
        pola = r'<w:style [^>]*w:styleId="%s"[^>]*>.*?</w:style>' % sid
        if re.search(pola, gaya, re.S):
            gaya = re.sub(pola, lambda _: xml, gaya, count=1, flags=re.S)
        else:
            gaya = gaya.replace("</w:styles>", xml + "</w:styles>")
    isi["word/styles.xml"] = gaya.encode("utf-8")

    doc = isi["word/document.xml"].decode("utf-8")
    doc = re.sub(r"<w:tbl>.*?</w:tbl>", lambda m: rapikan_tabel(m.group(0)), doc, flags=re.S)
    # Judul tabel di tengah & menempel ke tabelnya
    doc = re.sub(r'<w:p><w:pPr><w:pStyle w:val="(?:BodyText|FirstParagraph)" /></w:pPr>(<w:r><w:t xml:space="preserve">Tabel I\.)',
                 r'<w:p><w:pPr><w:pStyle w:val="BodyText" /><w:keepNext /><w:spacing w:before="120" w:after="120" /><w:jc w:val="center" /></w:pPr>\1',
                 doc)
    # Beri jarak antara tabel & paragraf sesudahnya
    doc = re.sub(r'</w:tbl>(\s*)<w:p><w:pPr><w:pStyle w:val="(BodyText|FirstParagraph)" />',
                 r'</w:tbl>\1<w:p><w:pPr><w:pStyle w:val="\2" /><w:spacing w:before="360" />', doc)
    doc = re.sub(r"<w:sectPr>.*?</w:sectPr>\s*</w:body>", "</w:body>", doc, flags=re.S)
    doc = doc.replace("</w:body>", SECT + "</w:body>", 1)
    doc = doc.replace("<w:body>", "<w:body>" + kepala(idn), 1)
    isi["word/document.xml"] = doc.encode("utf-8")

    isi["word/footer1.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<w:p><w:pPr><w:jc w:val="center" /></w:pPr>'
        '<w:r><w:fldChar w:fldCharType="begin" /></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate" /></w:r><w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end" /></w:r>'
        '</w:p></w:ftr>').encode("utf-8")
    rels = isi["word/_rels/document.xml.rels"].decode("utf-8")
    isi["word/_rels/document.xml.rels"] = rels.replace("</Relationships>",
        '<Relationship Id="rIdKakiHal" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" '
        'Target="footer1.xml" /></Relationships>').encode("utf-8")
    ct = isi["[Content_Types].xml"].decode("utf-8")
    isi["[Content_Types].xml"] = ct.replace("</Types>", '<Override PartName="/word/footer1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml" /></Types>').encode("utf-8")

    sementara = DOCX.with_suffix(".tmp.docx")
    with zipfile.ZipFile(sementara, "w", zipfile.ZIP_DEFLATED) as z:
        for nama, data in isi.items():
            z.writestr(nama, data)
    shutil.move(sementara, DOCX)
    print("==> Tata letak dirapikan: judul & identitas di atas I.1, tabel bergaris, nomor halaman di kaki")


main()
