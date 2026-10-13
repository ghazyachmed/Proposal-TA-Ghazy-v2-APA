#!/usr/bin/env python3
"""Salin isi docs/Konsultasi-Latar-Belakang.md ke Bab I LaTeX.

Bagian yang disalin: I.1 Latar Belakang sampai I.6 Metodologi. Teks di kedua
berkas jadi identik, sehingga DOCX konsultasi & PDF resmi tidak berbeda isi. Jalankan dari root repo:

    python3 tools/md-ke-babI.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "docs" / "Konsultasi-Latar-Belakang.md"
TEX = ROOT / "Bab I - Pendahuluan.tex"

# Judul tabel di Markdown -> label & format kolom di LaTeX
# Isi sel rata kiri supaya kolom sempit tidak berjarak lebar
R = r">{\raggedright\arraybackslash}"
TABEL = {
    "Perbedaan penelitian yang sudah ada dengan kasus WINGman": ("tab:penelitian-ada", f"|{R}p{{2.4cm}}|{R}X|{R}X|{R}p{{2.2cm}}|", "\\footnotesize"),
    # Kolom pertama hanya berisi huruf skenario, jadi selebar isinya saja
    "Skenario pengujian": ("tab:skenario", f"|l|{R}X|{R}X|"),
    # Kolom pustaka berhuruf kecil supaya fokus tetap pada tahap, teknik, kondisi sekarang, & kebutuhan
    "Tahapan, teknik, kondisi sekarang, kebutuhan, dan pustaka": ("tab:tahapan", f"|{R}p{{2.0cm}}|{R}p{{2.0cm}}|{R}X|{R}X|>{{\\raggedright\\arraybackslash\\footnotesize}}p{{2.8cm}}|"),
}
NOMOR = {"I.1": "tab:penelitian-ada", "I.2": "tab:tahapan"}


def inline(t):
    t = t.replace("%", r"\%").replace("&", r"\&").replace("_", r"\_")
    # Sitasi naratif dua penulis yang ditulis manual: "A dan B [-@kunci]"
    t = re.sub(r"[A-Z][\w-]+ dan [A-Z][\w-]+ \[-@([\w-]+)\]", r"\\textcite{\1}", t)
    # Sitasi ganda: [@a; @b] -> \autocite{a,b}
    t = re.sub(r"\[(@[\w-]+(?:;\s*@[\w-]+)+)\]",
               lambda m: "\\autocite{" + ",".join(k.strip()[1:] for k in m.group(1).split(";")) + "}", t)
    t = re.sub(r"\[@([\w-]+)\]", r"\\autocite{\1}", t)
    t = re.sub(r"@([A-Za-z][\w-]+)", r"\\textcite{\1}", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", t)
    t = re.sub(r"\*([^*]+)\*", r"\\emph{\1}", t)
    t = re.sub(r"Tabel (I\.\d)\b", lambda m: "Tabel~\\ref{" + NOMOR[m.group(1)] + "}", t)
    return t


def tabel_latex(judul, baris):
    label, kolom, *ukuran = TABEL[judul]
    sel = [[inline(c.strip()) for c in b.strip().strip("|").split("|")] for b in baris]
    kepala, isi = sel[0], sel[2:]
    n = len(kepala)
    # [!htbp] melonggarkan aturan float supaya tabel tetap dekat teksnya
    out = ["\\begin{table}[!htbp]", "  \\caption{" + judul + "}", "  \\label{" + label + "}",
           "  " + (ukuran[0] if ukuran else "\\small"), "  \\begin{tabularx}{\\textwidth}{" + kolom + "}", "    \\hline",
           "    " + " & ".join(kepala) + " \\\\", "    \\hline"]
    for i, r in enumerate(isi):
        out.append("    " + " & ".join(r) + " \\\\")
        lanjut = i + 1 < len(isi) and isi[i + 1][0] == ""
        out.append("    \\cline{2-" + str(n) + "}" if lanjut else "    \\hline")
    out += ["  \\end{tabularx}", "\\end{table}"]
    return "\n".join(out)


def ubah(blok):
    hasil, baris = [], blok.strip("\n").split("\n")
    i = 0
    while i < len(baris):
        b = baris[i]
        m = re.match(r"Tabel I\.\d (.+)$", b)
        if m and m.group(1) in TABEL:
            j = i + 1
            while j < len(baris) and not baris[j].startswith("|"):
                j += 1
            k = j
            while k < len(baris) and baris[k].startswith("|"):
                k += 1
            hasil.append(tabel_latex(m.group(1), baris[j:k]))
            i = k
            continue
        if re.match(r"\d+\. ", b):
            item = []
            while i < len(baris) and re.match(r"\d+\. ", baris[i]):
                item.append("\\item\t" + inline(re.sub(r"^\d+\. ", "", baris[i])))
                i += 1
            hasil.append("\\begin{enumerate}\n" + "\n".join(item) + "\n\\end{enumerate}")
            continue
        if b.startswith("- "):
            item = []
            while i < len(baris) and baris[i].startswith("- "):
                item.append("\\item\t" + inline(baris[i][2:]))
                i += 1
            hasil.append("\\begin{itemize}\n" + "\n".join(item) + "\n\\end{itemize}")
            continue
        hasil.append(inline(b) if b.strip() else "")
        i += 1
    teks = "\n".join(hasil)
    return re.sub(r"\n{3,}", "\n\n", teks).strip("\n") + "\n\n"


def bagian(md, judul):
    m = re.search(r"^# " + re.escape(judul) + r".*?$\n(.*?)(?=^# |\Z)", md, re.S | re.M)
    if not m:
        sys.exit("Bagian tidak ditemukan di Markdown: " + judul)
    return m.group(1)


def ganti(s, mulai, akhir, isi):
    i = s.index(mulai) + len(mulai)
    j = s.index(akhir, i)
    return s[:i] + isi + s[j:]


md = MD.read_text(encoding="utf-8")
tex = TEX.read_text(encoding="utf-8")
catatan = "% Isi bagian ini disalin otomatis dari docs/Konsultasi-Latar-Belakang.md oleh tools/md-ke-babI.py. Sunting Markdown-nya, lalu jalankan ulang.\n"
tex = ganti(tex, "\\section{Latar Belakang}\n", "% --- Rumusan Masalah ---", catatan + ubah(bagian(md, "I.1 Latar Belakang")))
tex = ganti(tex, "\\section{Rumusan Masalah}\n", "% --- Tujuan ---", catatan + ubah(bagian(md, "I.2 Rumusan Masalah")))
tex = ganti(tex, "\\section{Tujuan}\n", "% --- Batasan Masalah ---", catatan + ubah(bagian(md, "I.3 Tujuan")))
tex = ganti(tex, "\\section{Ruang Lingkup, Asumsi, dan Batasan Masalah}\n", "\\section{Hipotugas akhir}", catatan + ubah(bagian(md, "I.4 Ruang Lingkup")))
# Judul subbab "Hipotugas akhir" berasal dari template, tidak diubah skrip ini
tex = ganti(tex, "\\section{Hipotugas akhir}\n", "% --- Metodologi Pengerjaan TA ---", catatan + ubah(bagian(md, "I.5 Hipotesis")))
tex = ganti(tex, "\\section{Metodologi}\n", "% --- Sistematika Penulisan ---", catatan + ubah(bagian(md, "I.6 Metodologi")))
TEX.write_text(tex, encoding="utf-8")
print("Bab I diperbarui dari", MD.name)
