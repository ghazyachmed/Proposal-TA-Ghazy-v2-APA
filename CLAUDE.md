# CLAUDE.md

Panduan kerja untuk Claude Code di repo ini. Repo ini berisi Proposal Tugas Akhir
STI STEI ITB berbasis LaTeX (template `ta-sti.cls` oleh baskara@itb.ac.id).

## Perintah kompilasi

Jalankan dari root repo, berurutan, empat langkah (dua `xelatex` terakhir wajib
agar daftar isi, daftar gambar, nomor halaman, dan sitasi konvergen):

```bash
xelatex ProposalTA.tex && biber ProposalTA && xelatex ProposalTA.tex && xelatex ProposalTA.tex
```

- Mesin TeX wajib **XeLaTeX**, bukan pdflatex. Kelas memanggil `fontspec` dan
  `\setmainfont{Times New Roman}`, sehingga pdflatex pasti gagal.
- Backend bibliografi wajib **Biber**, bukan bibtex (`backend=biber` di kelas).
- Argumen `biber` tanpa ekstensi: `biber ProposalTA`, bukan `biber ProposalTA.tex`.
- Hasil akhir: `ProposalTA.pdf`.
- Jika sitasi muncul sebagai tanda tanya, hapus `ProposalTA.bcf` dan `ProposalTA.bbl`
  lalu ulangi keempat langkah dari awal.

## Identitas dokumen (judul, nama, NIM)

Judul, nama penulis, NIM, dan program studi didefinisikan **sekali** di blok
`IDENTITAS DOKUMEN` pada preamble `ProposalTA.tex`, lalu dipakai ulang lewat
`\judulta`, `\namapenulis`, `\nimpenulis`, dan `\prodita`.

- Sunting nilainya di `ProposalTA.tex` saja. Jangan menulis ulang judul atau nama
  langsung di `1 Halaman Judul.tex`.
- Dua kandidat judul disimpan berdampingan; yang aktif adalah `\newcommand` yang
  tidak diberi tanda komentar. Untuk berganti judul, pindahkan tanda `%`.
- Jangan mengaktifkan kedua `\newcommand{\judulta}` sekaligus — LaTeX menolak
  definisi ganda.
- `2 Lembar Pengesahan.tex` masih memuat nama contoh dan belum memakai perintah
  ini. Ubah hanya bila diminta.

## Ekspor ke DOCX

```bash
./tools/tex-to-docx.sh
```

Hasilnya `out/ProposalTA.docx`, peringatan pandoc di `out/pandoc.log`.

- Skrip ini **tidak pernah menyunting berkas repo**. Ia menyalin proyek ke
  direktori staging sementara, menormalkan bentuk `\input berkas.tex` (tanpa
  kurung kurawal, dipakai Bab II) menjadi `\input{berkas.tex}` karena pandoc
  menolak bentuk primitif itu, lalu mengonversi dari sana.
- Sitasi diproses dengan `--citeproc` memakai `tools/apa.csl`, sehingga gaya
  DOCX sama dengan gaya biblatex APA di `ta-sti.cls`. Berkas CSL diunduh otomatis
  pada eksekusi pertama.
- `tools/referensi-docx.docx` mengatur gaya Word (Times New Roman 12pt, spasi 1,5).
  Berkas ini dibuat otomatis dan boleh disunting sendiri di Word; hapus untuk
  mengembalikannya ke bawaan.
- Keterbatasan yang sudah diketahui: lingkungan `align` yang memuat `\intertext`
  atau komentar `%` di dalam rumus tidak dapat dikonversi dan tersalin sebagai
  TeX mentah. Lingkungan `algorithm` dan `lstlisting` juga tidak punya padanan
  penuh di Word.
- DOCX adalah keluaran tambahan untuk berbagi draf. Format resmi yang dinilai
  tetap PDF hasil XeLaTeX.

## Naskah utama di Google Docs

Naskah disunting di Google Doc berikut. Aturan ini berlaku untuk semua RoomChat,
lokal maupun cloud.

- Judul Doc: **"draft Proposal 18223093 Ghazy Achmed"**
- ID Doc: `1dvHYuSI2e3BaW_fjLCBIxPK_snFcrYrLdnsgkB4_OjI`
- Buka Doc dengan ID. Bila ID gagal dibuka, cari Doc lewat judulnya di Google Drive.

- Tab utama naskah adalah **"Prop TA"**. Susunannya mengikuti `ProposalTA.tex`
  utuh: halaman depan, Bab I sampai Bab V, Daftar Pustaka, dan Lampiran. Bab II
  sampai Bab V baru berisi judul subbab template. Tab "Poin", "Paragraf",
  "PERTANYAAN", dan "draft Scope" adalah bahan kerja penulis. Jangan menyunting
  tab itu tanpa permintaan.
- Sunting lewat konektor Google Docs (`read_doc`, `update_doc`). Selalu pakai
  `writeMode: SUGGEST`, sehingga setiap perubahan muncul sebagai saran yang
  diterima atau ditolak penulis. Mode `EDIT` hanya dipakai bila penulis memintanya.
- Baca dokumen dulu, lalu kirim `requiredRevisionId` dari bacaan terakhir. Bila
  revisi berubah, baca ulang. Jangan menebak indeks.
- Saran format (font, ukuran, tebal, miring) yang ditumpuk di atas teks sisipan
  yang masih berstatus saran bisa hilang saat penulis menerimanya. Teks lalu jatuh
  ke gaya bawaan Arial 11. Sesudah penulis menerima sisipan, baca ulang dokumen,
  bandingkan format per karakter, lalu sarankan format yang kurang.
- Format naskah mengikuti `ta-sti.cls`: A4, margin atas, bawah, dan kanan 3 cm,
  margin kiri 4 cm, Times New Roman, isi 12 pt, spasi 1,5, jarak antarparagraf 12 pt,
  judul bab 14 pt tebal di tengah, tabel 10 pt. Margin di `sectionStyle` menimpa
  margin `documentStyle`, jadi periksa keduanya. Gambar disisipkan lewat URL publik, misalnya
  berkas `raw.githubusercontent.com` dari repo ini, karena API tidak menerima berkas lokal.
- Hasil `read_doc` biasanya terlalu besar untuk konteks dan disimpan ke berkas.
  Olah berkas itu dengan Python atau jq, lalu cocokkan teks sebelum menghitung indeks.
- Tulis sitasi di Doc dalam format APA jadi, misalnya "(Kalai dkk. 2025)" atau
  "Macedo dkk. (2026)". Jangan menulis kunci seperti `[@kunci]`. Saat menyalin ke
  `.tex`, petakan sitasi ke kunci di `daftar-pustaka.bib`.
- Alur kerja: Claude menulis saran, penulis menerima atau menolak, penulis boleh
  menjalankan Paperpal sendiri, lalu sesi tex menyalin isi tab "Prop TA" yang sudah
  diterima ke berkas `.tex` bab yang sesuai dan mengompilasi PDF. Halaman depan
  dan Daftar Pustaka di Doc hanya cerminan; sumbernya tetap berkas frontmatter
  `.tex` dan `daftar-pustaka.bib`. Claude tidak bisa
  menjalankan Paperpal karena tidak ada konektornya.
- Jangan mengubah izin berbagi Doc, dan jangan menyalin isi Doc ke berkas lain yang
  di-commit ke repo publik.
- Bila sesi tidak punya alat Google Docs, minta penulis menyalakan konektor
  Google Drive di pengaturan Connectors claude.ai. Jangan menyunting Doc lewat
  cara lain.
- `docs/Konsultasi-Latar-Belakang.md` dan `tools/konsultasi-docx.sh` sudah usang
  sejak naskah pindah ke Google Docs.

## Aturan nama file berspasi

Banyak file bab dan frontmatter memakai spasi di namanya, misalnya
`Bab I - Pendahuluan.tex`, `1 Halaman Judul.tex`, `3a Deklarasi Penggunaan AI.tex`.

- **Jangan mengganti nama file yang sudah ada.** Nama file itu tertulis persis di
  `\input{...}` dalam `ProposalTA.tex`; mengubah nama akan memutus kompilasi.
- Di shell, selalu kutip nama file: `cat "Bab II - Studi.tex"`, bukan `cat Bab II - Studi.tex`.
  Hal ini berlaku juga untuk `git add`, `mv`, `grep`, dan editor CLI.
- Di LaTeX, ikuti pola yang sudah ada: `\input{Bab I - Pendahuluan.tex}` — nama
  lengkap di dalam kurung kurawal, ekstensi `.tex` ditulis eksplisit, tanpa tanda
  kutip tambahan. Gunakan `\input`, bukan `\include`.
- File baru sebaiknya memakai tanda hubung tanpa spasi (`Lampiran-B.tex`,
  `Bab VI-Penutup.tex`). Jika file baru tetap memakai spasi, daftarkan ke
  `ProposalTA.tex` dengan pola `\input{...}` yang sama.
- Hindari glob liar (`rm *.tex`, `mv Bab*`) karena spasi membuat pemecahan kata
  shell mudah salah sasaran.

## Jangan ubah `ta-sti.cls`

`ta-sti.cls` adalah file kelas resmi template dan **tidak boleh disunting**, termasuk
margin, spasi, format judul bab, gaya sitasi, dan daftar paket. Berkas ini menentukan
kepatuhan dokumen terhadap format resmi STI STEI ITB.

- Semua penyesuaian tampilan yang benar-benar perlu ditaruh di preamble
  `ProposalTA.tex` (setelah `\documentclass`), bukan di dalam kelas.
- Jika suatu kebutuhan hanya bisa dipenuhi dengan mengubah kelas, laporkan dulu ke
  pengguna beserta alasannya dan tunggu persetujuan; jangan sunting diam-diam.
- `README Latex-VSC.pdf` dan `.gitattributes` juga bukan milik pekerjaan penulisan;
  biarkan apa adanya.

## Gaya sitasi yang aktif

Gaya yang benar-benar aktif adalah **APA** (`style=apa, backend=biber` di
`ta-sti.cls:49-53`), bukan Chicago. Catatan `biblatex-chicago` di `README.md:65`
adalah sisa template lama dan tidak mencerminkan konfigurasi sekarang.

- Sitasi naratif: `\textcite{kunci}` → Saewong (2002).
- Sitasi parentetik: `\autocite{kunci}` → (Saewong, 2002).
- Kelas memetakan ulang `\cite` menjadi `\parencite`, jadi hindari `\cite` polos
  agar maksudnya tidak kabur; tulis `\textcite` atau `\autocite` secara eksplisit.
- Referensi baru ditambahkan ke `daftar-pustaka.bib` dalam format BibLaTeX.

## Aturan menulis Bahasa Indonesia (S-P-O-K)

Setiap kalimat isi bab ditulis dengan struktur **Subjek – Predikat – Objek – Keterangan**.

- Subjek wajib eksplisit. Salah: "Dalam penelitian ini membahas rancangan sistem."
  Benar: "Penelitian ini membahas rancangan sistem pada fasilitas kesehatan pedesaan."
- Satu kalimat memuat satu gagasan. Pecah kalimat yang melebihi kira-kira 25 kata
  alih-alih menumpuk anak kalimat.
- Predikat diletakkan dekat subjek; keterangan (waktu, tempat, cara, tujuan)
  ditaruh di akhir, kecuali penekanan menuntut sebaliknya.
- Gunakan kata baku sesuai KBBI dan ejaan EYD; hindari ragam lisan
  ("nggak", "kayak", "bikin") dan singkatan tidak resmi.
- Hindari "dimana", "yang mana", dan "di mana" sebagai penghubung ala bahasa Inggris;
  gunakan "yang", "tempat", atau pecah kalimatnya.
- Istilah asing dimiringkan: `\emph{machine learning}` atau `\textit{big data}`.
  Utamakan padanan Indonesia bila sudah baku (perangkat lunak, basis data, luaran).
- Gunakan kalimat aktif untuk menyatakan tindakan penulis atau sistem; kalimat pasif
  dipakai hanya bila pelaku tidak penting.
- Konsisten pada satu sudut pandang impersonal ("penulis", "penelitian ini");
  jangan memakai "saya" atau "kami" secara bergantian.

## Konteks repo singkat

- `ProposalTA.tex` — file utama, hanya berisi preamble ringkas dan rangkaian `\input`.
- `Bab I`–`Bab V`, `Lampiran-A.tex`, file frontmatter bernomor — isi tulisan, boleh disunting.
- `daftar-pustaka.bib` — daftar referensi BibLaTeX, boleh disunting.
- `ta-sti.cls` — kelas resmi, jangan disunting.
- `images/`, `tables/`, `listings/`, `algorithms/` — aset yang dipanggil dari bab.
- `tools/` — skrip pendukung; `tex-to-docx.sh` boleh disunting, aset unduhan di
  dalamnya dibuat ulang otomatis.
- `out/` — keluaran pipeline DOCX, diabaikan git.
- `Lampiran-B.tex` ada di repo tetapi belum di-`\input` dari `ProposalTA.tex`.
- Jangan mengubah isi bab apa pun tanpa permintaan eksplisit dari pengguna.

# Aturan kerja repo Proposal TA

## Konteks
Repo ini berisi proposal Tugas Akhir Prodi STI STEI ITB, mata kuliah II4091, pembimbing Windy Gambetta.
Topik: Wingman Assistant, chatbot Text-to-SQL untuk petroleum engineer production.

## Bahasa naskah
- Pakai S-P-O-K. Subjek jelas, kalimat aktif, 1 kalimat 1 ide, maksimal sekitar 20 kata
- Subjek nya benda nyata: sistem, chatbot, engineer, basis data, penulis
- Maksimal 1 istilah asing per kalimat & jelaskan saat pertama muncul
- Dilarang merangkai lebih dari 3 kata benda dalam 1 frasa
- Jangan mengubah wording, typing, atau ejaan penulis. Typo cukup didaftar terpisah, jangan diperbaiki sendiri

## Sesi kerja
- tex: menyunting file .tex, kompilasi, & merapikan sitasi
- data: restore dump ke PostgreSQL, menghitung, & menguji query
- docs: merawat file di folder docs
Sebut sesi nya di awal perintah. Jangan mencampur pekerjaan 2 sesi dalam 1 perintah.

## Kompilasi
xelatex ProposalTA.tex, lalu biber ProposalTA, lalu xelatex 2 kali.
Nama file bab mengandung spasi, jadi semua perintah wajib memakai tanda kutip.

## Sitasi
Gaya APA. ta-sti.cls sudah memakai style=apa & backend=biber. Paket yang dipakai biblatex-apa.
Jangan mengubah ta-sti.cls. Jangan menambah entri ke daftar-pustaka.bib tanpa data pustaka dari penulis.

## Angka & fakta
Semua angka hasil hitungan ditulis ke docs/01-FAKTA.md beserta kolom sumber, cara cek, & status.
Tambah baris di CHANGELOG paling bawah file itu: tanggal, angka yang ditambah, & sesi nya.
Perbarui baris "Update terakhir" di file yang berubah, lalu laporkan file mana yang perlu diupload ulang ke Konteks Project.

## Status dokumen konteks
Isi folder docs (00-STATE.md sampai 07-DRAFT-SCOPE.md, catatan, & salinan jawaban chat lain) adalah bahan kerja, BUKAN sumber kebenaran mutlak.
- Docs bisa salah atau usang. Contoh yang sudah terjadi: 202 Table (yang benar 206), status paper Spider-Ent "under review" (ternyata withdrawn), & sumber angka EntSQL 96,0% yang ditulis "abstract" padahal angka itu ada di teks penuh, bukan di abstrak
- Tiap klaim, angka, & keputusan tetap wajib punya justifikasi metode ilmiah: sumber primer (paper, dokumentasi resmi, kode, dump), metode yang bisa dikutip, atau validasi domain expert. "Sudah tertulis di docs" bukan justifikasi
- Kalau docs bertentangan dengan sumber primer, ikuti sumber primer, laporkan selisih nya, & jangan menimpa docs tanpa izin penulis
- Keputusan & daftar di docs yang belum punya dasar metode, contoh daftar Table scope, diperlakukan sebagai hipotesis kerja
- Paper yang aksesnya tertutup: ambil bagian publik (abstrak, data availability, catatan kaki, review), atau cari paper lain yang mengutip nya
- Pakai label VERIFIED, SEKUNDER, INFERENSI, & TIDAK TAHU untuk klaim yang status nya belum jelas

## Larangan
- Repo ini publik. Jangan commit folder docs & folder data, keduanya ada di .gitignore
- Jangan commit apa pun sebelum penulis memeriksa
- Jangan mematikan paket atau menghapus bagian naskah supaya kompilasi lolos