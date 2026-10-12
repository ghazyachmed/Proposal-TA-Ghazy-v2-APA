#!/usr/bin/env bash
#
# Pipeline LaTeX -> DOCX untuk Proposal Tugas Akhir.
#
# Pakai:
#   ./tools/tex-to-docx.sh              # hasil: out/ProposalTA.docx
#   ./tools/tex-to-docx.sh -o draf.docx # tentukan nama berkas keluaran
#
# Skrip ini TIDAK pernah menyunting berkas di repo. Seluruh penyesuaian
# dilakukan pada salinan sementara di direktori staging, lalu dibuang.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MAIN="ProposalTA.tex"
OUTDIR="$ROOT/out"
OUTFILE="$OUTDIR/ProposalTA.docx"
CSL="$ROOT/tools/apa.csl"
REFDOC="$ROOT/tools/referensi-docx.docx"
BIB="daftar-pustaka.bib"
CSL_URL="https://raw.githubusercontent.com/citation-style-language/styles/master/apa.csl"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--output) OUTFILE="$2"; shift 2 ;;
    -h|--help)   sed -n '3,12p' "$0"; exit 0 ;;
    *) echo "Argumen tidak dikenal: $1" >&2; exit 2 ;;
  esac
done

# --- 1. Prasyarat ---------------------------------------------------------
if ! command -v pandoc >/dev/null 2>&1; then
  echo "ERROR: pandoc belum terpasang. Pasang dengan: brew install pandoc" >&2
  exit 1
fi
[[ -f "$MAIN" ]] || { echo "ERROR: $MAIN tidak ditemukan di $ROOT" >&2; exit 1; }

mkdir -p "$OUTDIR" "$(dirname "$OUTFILE")"

# --- 2. Gaya sitasi APA ---------------------------------------------------
# Repo memakai biblatex style=apa, jadi DOCX-nya juga harus APA.
if [[ ! -f "$CSL" ]]; then
  echo "==> Mengunduh gaya APA dari repositori resmi CSL ..."
  if ! curl -fsSL -o "$CSL" "$CSL_URL"; then
    echo "ERROR: gagal mengunduh apa.csl. Unduh manual ke $CSL dari:" >&2
    echo "       $CSL_URL" >&2
    exit 1
  fi
fi

# --- 3. Templat gaya Word -------------------------------------------------
# Dibuat sekali, lalu boleh disunting sendiri di Word (ubah font, spasi,
# margin, gaya Heading). Hapus berkasnya untuk mengembalikan ke bawaan.
if [[ ! -f "$REFDOC" ]]; then
  echo "==> Membuat templat gaya Word (Times New Roman 12pt, spasi 1,5, rata kiri-kanan) ..."
  pandoc --print-default-data-file reference.docx > "$REFDOC"
  python3 - "$REFDOC" <<'PYEOF'
import re, shutil, sys, zipfile

path = sys.argv[1]
tmp = path + ".tmp"

TNR = ('<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" '
       'w:eastAsia="Times New Roman" w:cs="Times New Roman"/>')

def patch_docdefaults(xml):
    """Ubah HANYA blok docDefaults: ukuran badan 12pt dan spasi 1,5.

    Ukuran judul (Heading 1 dst.) sengaja tidak disentuh supaya hierarki
    visualnya tetap ada.
    """
    m = re.search(r"<w:docDefaults>.*?</w:docDefaults>", xml, re.S)
    if not m:
        return xml
    blok = m.group()
    asli = blok
    # Badan teks 12pt (24 half-point).
    blok = re.sub(r'<w:sz w:val="\d+"\s*/>', '<w:sz w:val="24"/>', blok)
    blok = re.sub(r'<w:szCs w:val="\d+"\s*/>', '<w:szCs w:val="24"/>', blok)
    # Spasi 1,5 = line 360 twip.
    def tambah_spasi(sm):
        tag = sm.group()
        if "w:line=" in tag:
            tag = re.sub(r'w:line="\d+"', 'w:line="360"', tag)
            tag = re.sub(r'w:lineRule="\w+"', 'w:lineRule="auto"', tag)
            return tag
        return tag.rstrip("/> ").rstrip() + ' w:line="360" w:lineRule="auto"/>'
    pm = re.search(r"<w:pPrDefault>.*?</w:pPrDefault>", blok, re.S)
    if pm:
        pblok = re.sub(r"<w:spacing[^>]*/>", tambah_spasi, pm.group())
        blok = blok.replace(pm.group(), pblok)
    return xml.replace(asli, blok)

def justify_body(xml):
    """Badan teks rata kiri-kanan (justify), sama dengan PDF template."""
    m = re.search(r'(<w:style [^>]*w:styleId="BodyText".*?)(</w:style>)', xml, re.S)
    if not m or "<w:jc " in m.group(1):
        return xml
    blok = m.group(1)
    if "<w:pPr>" in blok:
        baru = blok.replace("<w:pPr>", '<w:pPr><w:jc w:val="both"/>', 1)
    else:
        baru = blok + '<w:pPr><w:jc w:val="both"/></w:pPr>'
    return xml.replace(blok, baru, 1)

with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/styles.xml":
            xml = data.decode("utf-8")
            xml = re.sub(r"<w:rFonts[^>]*/>", TNR, xml)   # font: seluruh gaya
            xml = patch_docdefaults(xml)                   # ukuran + spasi: badan saja
            xml = justify_body(xml)                        # rata kiri-kanan: badan teks
            data = xml.encode("utf-8")
        zout.writestr(item, data)
shutil.move(tmp, path)
print("    templat gaya siap:", path)
PYEOF
fi

# --- 4. Staging -----------------------------------------------------------
# Template ini memakai bentuk primitif `\input berkas.tex` (tanpa kurung
# kurawal) di Bab II. XeLaTeX menerimanya, pandoc tidak. Bentuk itu
# dinormalkan di salinan, bukan di repo.
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

rsync -a --exclude='.git' --exclude='out' --exclude='tools' "$ROOT"/ "$STAGE"/

python3 - "$STAGE" <<'PYEOF'
import glob, os, re, sys
os.chdir(sys.argv[1])
n = 0
for f in glob.glob("**/*.tex", recursive=True):
    s = open(f, encoding="utf-8").read()
    s2 = re.sub(r'\\input\s+([^\s{}\\]+\.tex)', r'\\input{\1}', s)
    if s2 != s:
        open(f, "w", encoding="utf-8").write(s2)
        n += 1
print(f"    {n} berkas dinormalkan di staging (repo tidak disentuh)")
PYEOF

# --- 5. Konversi ----------------------------------------------------------
echo "==> Mengonversi $MAIN -> $OUTFILE ..."
LOG="$OUTDIR/pandoc.log"
(
  cd "$STAGE"
  pandoc "$MAIN" \
    --from=latex \
    --to=docx \
    --output="$OUTFILE" \
    --resource-path=".:images:tables:listings:algorithms" \
    --reference-doc="$REFDOC" \
    --citeproc \
    --bibliography="$BIB" \
    --csl="$CSL" \
    --toc \
    --toc-depth=3
) 2> >(tee "$LOG" >&2)

echo
echo "==> Selesai: $OUTFILE"
echo "    log peringatan: $LOG"
if grep -q "not found" "$LOG" 2>/dev/null; then
  echo
  echo "    CATATAN: ada kunci sitasi tanpa entri di $BIB."
  grep "not found" "$LOG" | sed 's/^/      /'
fi
