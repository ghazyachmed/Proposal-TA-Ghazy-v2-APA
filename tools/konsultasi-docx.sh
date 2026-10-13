#!/usr/bin/env bash
# Bangun DOCX konsultasi (judul, I.1, I.4, I.6) dari docs/Konsultasi-Latar-Belakang.md,
# lalu salin seluruh I.1-I.6 ke Bab I LaTeX.
# Jalankan dari mana saja: ./tools/konsultasi-docx.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
MD="docs/Konsultasi-Latar-Belakang.md"
OUT="docs/Konsultasi-Latar-Belakang.docx"
# Pengaman: sejak 13 Okt 2026 Bab I bisa disunting langsung di .tex (sesi lain).
# Kalau .tex lebih baru dari Markdown, skrip berhenti supaya Bab I & DOCX tidak tertimpa versi lama.
# Samakan Markdown dulu, atau jalankan dengan PAKSA=1 bila yakin Markdown yang benar.
if [[ "Bab I - Pendahuluan.tex" -nt "$MD" && "${PAKSA:-0}" != "1" ]]; then
  echo "BERHENTI: 'Bab I - Pendahuluan.tex' lebih baru dari $MD. Bab I & DOCX tidak diubah." >&2
  exit 1
fi
BIBS=(--bibliography daftar-pustaka.bib)
# Entri usulan yang belum disetujui ikut dipakai di DOCX konsultasi saja
[[ -f docs/usulan-pustaka-2.bib ]] && BIBS+=(--bibliography docs/usulan-pustaka-2.bib)
# DOCX konsultasi hanya memuat bagian berikut. Bab I LaTeX tetap memuat semua bagian dari Markdown yang sama
BAGIAN_KONSULTASI=(I.1 I.4 I.6)
KERJA="$(mktemp -d)"
trap 'rm -rf "${KERJA:?}"' EXIT
MD_KONSULTASI="$KERJA/konsultasi.md"
python3 - "$MD" "$MD_KONSULTASI" "${BAGIAN_KONSULTASI[@]}" <<'PYEOF'
import re, sys
sumber, tujuan, *pilih = sys.argv[1:]
teks = open(sumber, encoding="utf-8").read()
kepala, *bagian = re.split(r"(?m)^(?=# )", teks)
open(tujuan, "w", encoding="utf-8").write(kepala + "".join(b for b in bagian if b.split()[1] in pilih))
PYEOF
pandoc "$MD_KONSULTASI" --citeproc "${BIBS[@]}" --csl tools/apa.csl \
  --lua-filter tools/sitasi-ta-sti.lua \
  --reference-doc tools/referensi-docx.docx -o "$OUT"
# Judul & identitas di atas I.1 (dari blok IDENTITAS DOKUMEN ProposalTA.tex), gaya teks, tabel, & nomor halaman
python3 tools/tata-letak-konsultasi.py "$OUT"
echo "==> DOCX: $OUT"
python3 tools/md-ke-babI.py
